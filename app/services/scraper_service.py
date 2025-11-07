from typing import Optional, Dict
import subprocess
import json
import os
from datetime import datetime
from openai import OpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL
from app.models.player_info import PlayerInfoResponse


class ScraperService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.url = "https://www.espncricinfo.com/ci/content/player/"
        self.node_scraper_path = os.path.join(os.path.dirname(__file__), 'scrape.js')
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.openai_model = OPENAI_MODEL

    async def scrape_player_data(self, cricinfo_id: int, player_id: str) -> Optional[Dict]:
        result = await self.scrape_player_with_ai(cricinfo_id)
        if not result:
            raise Exception("No data returned from scraper")
        await self.db_manager.add_player(player_id, result['player_info'])
        return result

    async def _scrape_html_with_nodejs(self, cricinfo_id: int) -> Optional[Dict]:
        temp_script = f"""
            const {{ scrapePlayerHTML }} = require('{self.node_scraper_path}');

            async function main() {{
                try {{
                    const result = await scrapePlayerHTML('{cricinfo_id}');
                    console.log(JSON.stringify(result));
                }} catch (error) {{
                    console.error('Error:', error.message);
                    process.exit(1);
                }}
            }}

            main();
        """
        
        temp_file = '/tmp/temp_scraper.js'
        try:
            with open(temp_file, 'w') as f:
                f.write(temp_script)
            
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=os.path.dirname(self.node_scraper_path),
                env=os.environ.copy()
            )
            
            if result.returncode == 0:
                scraped_data = json.loads(result.stdout.strip())
                return scraped_data
            else:
                error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                # Raise exception with error message - 403 errors will be caught and retried
                raise Exception(f"Node.js scraper failed: {error_msg}")
        finally:
            # Always clean up temp file
            if os.path.exists(temp_file):
                os.remove(temp_file)

    async def _extract_player_info_with_openai(self, html: str) -> Optional[Dict]:
        prompt = f"""
            You are a cricket information expert with comprehensive knowledge of international and domestic cricket players.
            You are given a HTML page of a cricket player.
            Your task is to extract the player information from the HTML page.

            Instructions:
            - Provide accurate real-world information based on the HTML page
            - Ensure all information is factual and up-to-date
            - Include personal details, cricket-specific information, and career background

            Required information to provide:
            - Personal details (full name, birth info, physical attributes)
            - Cricket-specific information (batting/bowling style, role)

            HTML Content:
            {html}
        """

        completion = self.openai_client.chat.completions.parse(
            model=self.openai_model,
            messages=[
                {"role": "system", "content": "You are a cricket information extraction expert. Extract structured data from HTML."},
                {"role": "user", "content": prompt}
            ],
            response_format=PlayerInfoResponse,
        )

        player_info = completion.choices[0].message.parsed
        
        return player_info.model_dump()

    async def scrape_player_with_ai(self, cricinfo_id: int) -> Optional[Dict]:
        # Step 1: Use Node.js to scrape HTML
        scraped_data = await self._scrape_html_with_nodejs(cricinfo_id)
        if not scraped_data:
            raise Exception("No scraped data received from scraper")
        
        html = scraped_data.get('html')
        if not html:
            raise Exception("No HTML content received from scraper")
        
        # Step 2: Use Python/OpenAI to extract player information
        player_info = await self._extract_player_info_with_openai(html)
        if not player_info:
            raise Exception("No player info received from OpenAI")
        
        # Convert date string to date object
        player_info['dob'] = datetime.strptime(player_info['dob'], '%Y-%m-%d').date()
        
        return {
            'player_info': player_info,
            'scraped_at': scraped_data.get('scraped_at')
        }

