from typing import Optional, Dict
import requests
from datetime import datetime

class ScraperService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.url = "http://core.espnuk.org/v2/sports/cricket/athletes/"

    async def scrape_player_data(self, player_id: str, cricinfo_id: int) -> Optional[Dict]:
        try:
            response = requests.get(self.url + str(cricinfo_id))

            data = response.json()

            if not data:
                return None

            batting_styles = []
            bowling_styles = []
            styles = data['styles'] or []
            for style in styles:
                if style['type'] == 'batting':
                    batting_styles.append(style['description'])
                if style['type'] == 'bowling':
                    bowling_styles.append(style['description'])

            national_team = requests.get(data['team']['$ref']).json()['name'] if data['team'] else None

            player_data = {
                'name': data['name'] if data['name'] else None,
                'dob': datetime.strptime(data['dateOfBirth'], '%Y-%m-%dT%H:%MZ').date() if data['dateOfBirth'] else None,
                'batting_styles': batting_styles,
                'bowling_styles': bowling_styles,
                'playing_role': data['position']['name'] if data['position'] else None,
                'image_url': data['headshot']['href'] if data['headshot'] else None,
                'is_active': data['isActive'] if data['isActive'] else None,
                'gender': data['gender'] if data['gender'] else None,
                'national_team': national_team if national_team else None,
            }

            return player_data
        except Exception as e:
            print(f"Error scraping player {player_id}: {e}")
            return None


