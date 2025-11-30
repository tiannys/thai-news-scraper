from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import yaml
from pathlib import Path

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.api import articles_router, trends_router, sources_router
from app.services import scheduler_service
from app.models import Source
from sqlalchemy import select

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Starting Thai News Scraper API")
    
    try:
        # Initialize database
        await init_db()
        logger.info("Database initialized")
        
        # Load sources from config
        await load_sources_from_config()
        
        # Start scheduler
        scheduler_service.start()
        logger.info("Scheduler started")
        
        yield
    
    finally:
        # Shutdown
        logger.info("Shutting down Thai News Scraper API")
        scheduler_service.shutdown()


async def load_sources_from_config():
    """Load news sources from YAML config file"""
    try:
        config_path = Path(settings.sources_config_path)
        
        if not config_path.exists():
            logger.warning(f"Sources config file not found: {config_path}")
            return
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config or 'sources' not in config:
            logger.warning("No sources found in config file")
            return
        
        async with AsyncSessionLocal() as db:
            for source_config in config['sources']:
                # Check if source already exists
                result = await db.execute(
                    select(Source).where(Source.url == source_config['url'])
                )
                existing = result.scalar_one_or_none()
                
                if not existing:
                    # Create new source
                    source = Source(
                        name=source_config['name'],
                        type=source_config['type'],
                        url=source_config['url'],
                        category=source_config.get('category'),
                        country=source_config.get('country', 'TH'),
                        language=source_config.get('language', 'th'),
                        is_active=True
                    )
                    db.add(source)
                    logger.info(f"Added source: {source.name}")
            
            await db.commit()
            logger.info("Sources loaded from config")
    
    except Exception as e:
        logger.error(f"Error loading sources from config: {e}")


# Create FastAPI app
app = FastAPI(
    title="Thai News Scraper API",
    description="API for scraping and analyzing Thai news sources",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception handler caught: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "scheduler": "running" if scheduler_service.scheduler.running else "stopped"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Thai News Scraper API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


# Include routers
app.include_router(articles_router)
app.include_router(trends_router)
app.include_router(sources_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload
    )
