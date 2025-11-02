from typing import List, Tuple
from celery_app import app
import time
import asyncio
import config
from services.web.scraper import ScraperService
from services.db.manager import DatabaseService
import logging

logger = logging.getLogger(__name__)

db_service = DatabaseService(
    user=config.DB_USER,
    password=config.DB_PASSWORD,
    host=config.DB_HOST,
    dbname=config.DB_NAME,
    port=config.DB_PORT
)
scraper_service = ScraperService(db_service)

@app.task(bind=True, max_retries=3, default_retry_delay=60, name='scrape_player_data')
def scrape_player_task(self, cricinfo_id: int, player_id: str):
    logger.info(f"Scraping player data for {player_id} with cricinfo_id {cricinfo_id}")
    
    try: 
        result = asyncio.run(scraper_service.scrape_player_data(cricinfo_id, player_id))
        time.sleep(1)
        if result:
            return {
                'player_id': player_id,
                'status': 'success',
                'data': result
            }
        raise Exception("No result found")
    except Exception as e:
        logger.error(f"Error scraping player data for {player_id} with cricinfo_id {cricinfo_id}: {e}")
        raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))

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

