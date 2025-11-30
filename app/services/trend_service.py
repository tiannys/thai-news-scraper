from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict
from datetime import datetime, date, timedelta
from collections import Counter
import logging
from app.models import Article, Trend

logger = logging.getLogger(__name__)


class TrendService:
    """Trend extraction and analysis"""
    
    async def extract_trends_for_date(
        self,
        db: AsyncSession,
        target_date: date,
        min_frequency: int = 2
    ) -> List[Trend]:
        """Extract trending keywords for a specific date"""
        try:
            # Get articles for the date
            start_datetime = datetime.combine(target_date, datetime.min.time())
            end_datetime = datetime.combine(target_date, datetime.max.time())
            
            result = await db.execute(
                select(Article).where(
                    and_(
                        Article.published_at >= start_datetime,
                        Article.published_at <= end_datetime
                    )
                )
            )
            articles = result.scalars().all()
            
            if not articles:
                logger.info(f"No articles found for {target_date}")
                return []
            
            # Collect all keywords/tags
            keyword_articles = {}  # keyword -> list of article IDs
            
            for article in articles:
                if article.tags:
                    for tag in article.tags:
                        if tag not in keyword_articles:
                            keyword_articles[tag] = []
                        keyword_articles[tag].append(article.id)
            
            # Count frequencies
            keyword_freq = {k: len(v) for k, v in keyword_articles.items()}
            
            # Filter by minimum frequency
            trending_keywords = {k: v for k, v in keyword_freq.items() if v >= min_frequency}
            
            # Create or update trend records
            trends = []
            for keyword, frequency in trending_keywords.items():
                # Check if trend already exists
                existing = await db.execute(
                    select(Trend).where(
                        and_(
                            Trend.date == target_date,
                            Trend.keyword == keyword
                        )
                    )
                )
                trend = existing.scalar_one_or_none()
                
                if trend:
                    # Update existing
                    trend.frequency = frequency
                    trend.article_ids = keyword_articles[keyword]
                    trend.updated_at = datetime.utcnow()
                else:
                    # Create new
                    trend = Trend(
                        date=target_date,
                        keyword=keyword,
                        frequency=frequency,
                        article_ids=keyword_articles[keyword]
                    )
                    db.add(trend)
                
                trends.append(trend)
            
            await db.commit()
            
            logger.info(f"Extracted {len(trends)} trends for {target_date}")
            return trends
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Error extracting trends for {target_date}: {e}")
            return []
    
    async def get_trends_for_date(
        self,
        db: AsyncSession,
        target_date: date,
        limit: int = 20
    ) -> List[Trend]:
        """Get top trends for a specific date"""
        try:
            result = await db.execute(
                select(Trend)
                .where(Trend.date == target_date)
                .order_by(Trend.frequency.desc())
                .limit(limit)
            )
            trends = result.scalars().all()
            
            return trends
        
        except Exception as e:
            logger.error(f"Error getting trends for {target_date}: {e}")
            return []
    
    async def get_trending_categories(
        self,
        db: AsyncSession,
        since: datetime,
        limit: int = 10
    ) -> List[Dict]:
        """Get trending categories"""
        try:
            result = await db.execute(
                select(
                    Article.category,
                    func.count(Article.id).label('count')
                )
                .where(Article.published_at >= since)
                .group_by(Article.category)
                .order_by(func.count(Article.id).desc())
                .limit(limit)
            )
            
            categories = [
                {'category': row[0], 'count': row[1]}
                for row in result.all()
            ]
            
            return categories
        
        except Exception as e:
            logger.error(f"Error getting trending categories: {e}")
            return []
    
    async def get_top_sources(
        self,
        db: AsyncSession,
        since: datetime,
        limit: int = 10
    ) -> List[Dict]:
        """Get most active sources"""
        try:
            result = await db.execute(
                select(
                    Article.source_id,
                    func.count(Article.id).label('count')
                )
                .where(Article.published_at >= since)
                .group_by(Article.source_id)
                .order_by(func.count(Article.id).desc())
                .limit(limit)
            )
            
            sources = [
                {'source_id': row[0], 'article_count': row[1]}
                for row in result.all()
            ]
            
            return sources
        
        except Exception as e:
            logger.error(f"Error getting top sources: {e}")
            return []
