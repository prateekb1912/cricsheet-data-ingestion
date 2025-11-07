from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

from app.services.database import DatabaseService
from app.services.file_service import FileService
from app.routers import ingestion_router, crud_router, admin_router
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT

logger = logging.getLogger(__name__)

# Initialize services
db_service = DatabaseService(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    dbname=DB_NAME,
    port=DB_PORT
)
file_service = FileService(db_service)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    await db_service.initialize()
    yield


# Create FastAPI app
app = FastAPI(
    title="CricBit API",
    description="Cricket data management system",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(crud_router)
app.include_router(ingestion_router)
app.include_router(admin_router)

