from typing import List, Tuple
from app.celery_app import app
import time
import asyncio
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
from app.services.scraper_service import ScraperService
from app.services.database import DatabaseService
import logging

logger = logging.getLogger(__name__)

db_service = DatabaseService(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    dbname=DB_NAME,
    port=DB_PORT
)
scraper_service = ScraperService(db_service)

@app.task(bind=True, max_retries=3, default_retry_delay=300, name='scrape_player_data')
def scrape_player_task(self, cricinfo_id: int, player_id: str):
    logger.info(f"Scraping player data for {player_id} with cricinfo_id {cricinfo_id}")
    
    try: 
        result = asyncio.run(scraper_service.scrape_player_data(cricinfo_id, player_id))
        time.sleep(1)
        
        # Fail if no data is returned
        if not result:
            raise Exception("No data returned from scraper")
        
        return {
            'player_id': player_id,
            'status': 'success',
            'data': result
        }
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error scraping player data for {player_id} with cricinfo_id {cricinfo_id}: {e}")
        
        if '403' in error_message:
            raise self.retry(exc=e, countdown=300 * (2 ** self.request.retries))
        else:
            raise

@app.task
def scrape_all_players(player_ids: List[Tuple[str, int]]):
    results = []
    for (player_id, cricinfo_id) in player_ids:
        print(player_id, cricinfo_id)
        result = scrape_player_task.delay(cricinfo_id, player_id)
        print(result)
        results.append((player_id, result))
    return {
        'total': len(player_ids),
        'task_ids': results
    }

