from typing import Optional, Dict
import requests
import subprocess
import json
import os
from datetime import datetime

class ScraperService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.url = "https://www.espncricinfo.com/ci/content/player/"
        self.node_scraper_path = os.path.join(os.path.dirname(__file__), 'scrape.js')

    async def scrape_player_data(self, cricinfo_id: int, player_id: str) -> Optional[Dict]:
        try:
            result =  await self.scrape_player_with_ai(cricinfo_id)
            await self.db_manager.add_player(player_id, result['player_info'])
            return result
        except Exception as e:
            print(f"Error scraping player data: {e}")
            return None

    async def scrape_player_with_ai(self, cricinfo_id: int) -> Optional[Dict]:
        try:            
            temp_script = f"""
                const {{ scrapePlayerInfoWithAI }} = require('{self.node_scraper_path}');

                async function main() {{
                    try {{
                        const result = await scrapePlayerInfoWithAI('{cricinfo_id}');
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

            print("result.stdout", result.stdout)
            
            os.remove(temp_file)
            
            if result.returncode == 0:
                player_data = json.loads(result.stdout.strip())
                player_data['player_info']['dob'] = datetime.strptime(player_data['player_info']['dob'], '%Y-%m-%d').date()
                print(f"Successfully extracted data for: {player_data.get('player_info', {}).get('name', 'Unknown')}")
                return player_data
            else:
                print(f"Node.js scraper failed: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error calling Node.js scraper: {e}")
            return None
