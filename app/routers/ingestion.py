import logging
from fastapi import APIRouter, Request, HTTPException, Depends

from app.tasks.player_tasks import scrape_player_task

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingestion"])

def get_file_service():
    from app.main import file_service
    return file_service


def get_db_service():
    from app.main import db_service
    return db_service


@router.post("/matches")
async def add_matches(request: Request, file_service=Depends(get_file_service)):
    try:
        body = await request.json()
        url = body.get('url')
        if not url:
            raise HTTPException(status_code=400, detail="No URL provided")

        match_ids = await file_service.process_matches_url(url)
        if not match_ids:
            raise HTTPException(status_code=400, detail="No matches found or error processing matches")

        return {
            "status": "ok",
            "total_matches_processed": len(match_ids)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/match/{match_id}")
async def insert_match(match_id: int, request: Request, db_service=Depends(get_db_service)):
    try:
        body = await request.json()
        match_data = body.get('match_data')
        if not match_data:
            raise HTTPException(status_code=400, detail="No match data provided")

        await db_service.insert_match(match_id, match_data)
        return {
            "status": "ok",
            "data": {
                "match_id": match_id
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/players")
async def add_players(file_service=Depends(get_file_service), db_service=Depends(get_db_service)):
    await file_service.process_players_url()
    return {
        "status": "ok",
        "data": {
            "players_count": await db_service.get_players_count()
        }
    }


@router.post("/player/{player_id}")
async def add_player(player_id: str, file_service=Depends(get_file_service)):
    players_df = await file_service.get_players_df()
    player = players_df[players_df['identifier'] == player_id]

    if player.empty:
        raise HTTPException(status_code=404, detail="Player not found")    

    cricinfo_keys = file_service._get_cricinfo_keys(player.iloc[0])

    data = None
    for cricinfo_key in cricinfo_keys:
        result = scrape_player_task.delay(cricinfo_key, player_id)
        logger.info(f"Task result: {result}")
        try:
            task_result = result.get(timeout=30)
            logger.info(f"Task result: {task_result}")
            if task_result and task_result.get('data'):
                data = task_result.get('data')
                break
        except Exception as e:
            print(f"Error waiting for task result: {e}")
            continue

    if not data:
        raise HTTPException(status_code=500, detail="Failed to scrape player data")

    return {
        "status": "ok",
        "data": {
            "player_id": player_id,
            "scraped_player_info": data
        }
    }

