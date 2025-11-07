from fastapi import APIRouter, Depends

router = APIRouter(tags=["admin"])


def get_db_service():
    """Dependency to get DatabaseService instance"""
    from app.main import db_service
    return db_service


@router.post("/db/initialize")
async def initialize_db(db_service=Depends(get_db_service)):
    """Initialize database tables"""
    await db_service.initialize()
    return {
        "status": "ok"
    }

