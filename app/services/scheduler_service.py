from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, date
import logging
from app.config import settings
from app.database import AsyncSessionLocal
from app.services.article_service import ArticleService
from app.services.trend_service import TrendService

logger = logging.getLogger(__name__)


class SchedulerService:
    """APScheduler service for automated scraping"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.article_service = ArticleService()
        self.trend_service = TrendService()
    
    async def fetch_articles_job(self):
        """Scheduled job to fetch articles from all sources"""
        try:
            logger.info("Starting scheduled article fetch")
            
            async with AsyncSessionLocal() as db:
                results = await self.article_service.fetch_from_all_sources(db)
                logger.info(f"Fetch completed: {results['total_new']} new articles")
        
        except Exception as e:
            logger.error(f"Error in scheduled fetch job: {e}")
    
    async def extract_trends_job(self):
        """Scheduled job to extract daily trends"""
        try:
            logger.info("Starting trend extraction")
            
            async with AsyncSessionLocal() as db:
                today = date.today()
                trends = await self.trend_service.extract_trends_for_date(db, today)
                logger.info(f"Extracted {len(trends)} trends for {today}")
        
        except Exception as e:
            logger.error(f"Error in trend extraction job: {e}")
    
    def start(self):
        """Start the scheduler"""
        if not settings.scheduler_enabled:
            logger.info("Scheduler is disabled in settings")
            return
        
        try:
            # Schedule article fetching
            self.scheduler.add_job(
                self.fetch_articles_job,
                trigger=IntervalTrigger(minutes=settings.scheduler_fetch_interval_minutes),
                id='fetch_articles',
                name='Fetch articles from all sources',
                replace_existing=True
            )
            
            # Schedule trend extraction (daily at 23:00)
            self.scheduler.add_job(
                self.extract_trends_job,
                trigger=CronTrigger(hour=23, minute=0),
                id='extract_trends',
                name='Extract daily trends',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("Scheduler shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {e}")
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()


# Global scheduler instance
scheduler_service = SchedulerService()
