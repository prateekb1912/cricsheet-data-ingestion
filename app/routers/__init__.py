from app.routers.ingestion import router as ingestion_router
from app.routers.crud import router as crud_router
from app.routers.admin import router as admin_router

__all__ = ['ingestion_router', 'crud_router', 'admin_router']

