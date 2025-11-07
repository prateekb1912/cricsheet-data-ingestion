from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(tags=["crud"])


def get_db_service():
    """Dependency to get DatabaseService instance"""
    from app.main import db_service
    return db_service


@router.get("/")
async def root(db_service=Depends(get_db_service)):
    """Root endpoint with system stats"""
    total_matches = await db_service.get_total_matches()
    return {
        "status": "ok",
        "total_matches": total_matches
    }


@router.get("/match/count")
async def get_total_matches(db_service=Depends(get_db_service)):
    """Get total match count"""
    matches_count = await db_service.get_total_matches()
    return {
        "status": "ok",
        "data": {
            "total_matches": matches_count
        }
    }


@router.get("/match/{match_id}")
async def get_match_by_id(match_id: int, db_service=Depends(get_db_service)):
    """Get match by ID"""
    match = await db_service.get_match_by_id(match_id)
    return {
        "status": "ok",
        "data": {
            "match": match
        }
    }


@router.get("/player/{player_id}")
async def get_player_by_id(player_id: str, db_service=Depends(get_db_service)):
    """Get player by ID"""
    player = await db_service.get_player_by_id(player_id)
    return {
        "status": "ok",
        "data": {
            "player": player
        }
    }

