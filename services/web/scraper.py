from typing import Optional, Dict
import subprocess
import json
import os
from datetime import datetime
from openai import OpenAI
import config
from domains.player_info import PlayerInfoResponse


class ScraperService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.url = "https://www.espncricinfo.com/ci/content/player/"
        self.node_scraper_path = os.path.join(os.path.dirname(__file__), 'scrape.js')
        self.openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.openai_model = config.OPENAI_MODEL

    async def scrape_player_data(self, cricinfo_id: int, player_id: str) -> Optional[Dict]:
        try:
            result = await self.scrape_player_with_ai(cricinfo_id)
            await self.db_manager.add_player(player_id, result['player_info'])
            return result
        except Exception as e:
            print(f"Error scraping player data: {e}")
            return None

    async def _scrape_html_with_nodejs(self, cricinfo_id: int) -> Optional[Dict]:
        try:            
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
            
            os.remove(temp_file)
            
            if result.returncode == 0:
                scraped_data = json.loads(result.stdout.strip())
                return scraped_data
            else:
                print(f"Node.js scraper failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error calling Node.js scraper: {e}")
            return None

    async def _extract_player_info_with_openai(self, html: str) -> Optional[Dict]:
        try:
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

            completion = self.openai_client.beta.chat.completions.parse(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "You are a cricket information extraction expert. Extract structured data from HTML."},
                    {"role": "user", "content": prompt}
                ],
                response_format=PlayerInfoResponse,
            )

            player_info = completion.choices[0].message.parsed
            
            return player_info.model_dump()
            
        except Exception as e:
            print(f"Error extracting player info with OpenAI: {e}")
            return None

    async def scrape_player_with_ai(self, cricinfo_id: int) -> Optional[Dict]:
        try:
            # Step 1: Use Node.js to scrape HTML
            scraped_data = await self._scrape_html_with_nodejs(cricinfo_id)
            if not scraped_data:
                return None
            
            html = scraped_data.get('html')
            if not html:
                print("No HTML content received from scraper")
                return None
            
            # Step 2: Use Python/OpenAI to extract player information
            player_info = await self._extract_player_info_with_openai(html)
            if not player_info:
                return None
            
            # Convert date string to date object
            player_info['dob'] = datetime.strptime(player_info['dob'], '%Y-%m-%d').date()
            
            print(f"Successfully extracted data for: {player_info.get('name', 'Unknown')}")
            
            return {
                'player_info': player_info,
                'scraped_at': scraped_data.get('scraped_at')
            }
                
        except Exception as e:
            print(f"Error in scrape_player_with_ai: {e}")
            return None
