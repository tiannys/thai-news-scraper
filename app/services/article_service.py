from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging
from app.models import Article, Source
from app.schemas import ArticleCreate, ArticleResponse
from app.scraper import RSSParser, DataNormalizer, Deduplicator

logger = logging.getLogger(__name__)


class ArticleService:
    """Business logic for article management"""
    
    def __init__(self):
        self.rss_parser = RSSParser()
        self.normalizer = DataNormalizer()
        self.deduplicator = Deduplicator()
    
    async def get_articles(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        since: Optional[datetime] = None,
        category: Optional[str] = None
    ) -> List[Article]:
        """Get articles with optional filters"""
        try:
            query = select(Article)
            
            # Apply filters
            conditions = []
            if since:
                conditions.append(Article.created_at >= since)
            if category:
                conditions.append(Article.category == category)
            
            if conditions:
                query = query.where(and_(*conditions))
            
            # Order by published date (most recent first)
            query = query.order_by(Article.published_at.desc())
            
            # Pagination
            query = query.offset(skip).limit(limit)
            
            result = await db.execute(query)
            articles = result.scalars().all()
            
            return articles
        
        except Exception as e:
            logger.error(f"Error getting articles: {e}")
            return []
    
    async def get_article_by_id(self, db: AsyncSession, article_id: int) -> Optional[Article]:
        """Get a single article by ID"""
        try:
            result = await db.execute(select(Article).where(Article.id == article_id))
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting article {article_id}: {e}")
            return None
    
    async def create_article(self, db: AsyncSession, article_data: dict) -> Optional[Article]:
        """Create a new article"""
        try:
            # Normalize data
            normalized = self.normalizer.normalize_article(article_data)
            
            # Add content hash
            normalized = self.deduplicator.add_hash_to_article(normalized)
            
            # Create article
            article = Article(**normalized)
            db.add(article)
            await db.commit()
            await db.refresh(article)
            
            return article
        
        except Exception as e:
            await db.rollback()
            logger.error(f"Error creating article: {e}")
            return None
    
    async def get_existing_hashes(self, db: AsyncSession, since: Optional[datetime] = None) -> set:
        """Get set of existing content hashes for deduplication"""
        try:
            query = select(Article.content_hash)
            
            if since:
                query = query.where(Article.created_at >= since)
            
            result = await db.execute(query)
            hashes = {row[0] for row in result.all()}
            
            return hashes
        
        except Exception as e:
            logger.error(f"Error getting existing hashes: {e}")
            return set()
    
    async def fetch_from_source(self, db: AsyncSession, source: Source) -> int:
        """Fetch articles from a single source"""
        try:
            logger.info(f"Fetching from source: {source.name} ({source.url})")
            
            # Get existing hashes (last 7 days to avoid checking entire DB)
            since = datetime.utcnow() - timedelta(days=7)
            existing_hashes = await self.get_existing_hashes(db, since)
            
            # Fetch and parse articles
            if source.type == 'rss':
                articles_data = await self.rss_parser.parse_feed(
                    source.url,
                    source.id,
                    source.category
                )
            else:
                logger.warning(f"Source type {source.type} not yet implemented")
                return 0
            
            # Process articles
            new_count = 0
            for article_data in articles_data:
                # Normalize
                normalized = self.normalizer.normalize_article(article_data)
                
                # Check for duplicates
                normalized = self.deduplicator.add_hash_to_article(normalized)
                
                if normalized['content_hash'] not in existing_hashes:
                    # Create article
                    article = await self.create_article(db, normalized)
                    if article:
                        new_count += 1
                        existing_hashes.add(normalized['content_hash'])
            
            # Update source last_fetched_at
            source.last_fetched_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Fetched {new_count} new articles from {source.name}")
            return new_count
        
        except Exception as e:
            logger.error(f"Error fetching from source {source.name}: {e}")
            return 0
    
    async def fetch_from_all_sources(self, db: AsyncSession) -> dict:
        """Fetch articles from all active sources"""
        try:
            # Get all active sources
            result = await db.execute(
                select(Source).where(Source.is_active == True)
            )
            sources = result.scalars().all()
            
            total_new = 0
            results = {}
            new_articles = []
            
            for source in sources:
                count = await self.fetch_from_source(db, source)
                total_new += count
                results[source.name] = count
            
            # Get newly created articles for webhook notification
            if total_new > 0:
                # Fetch articles created in the last minute
                recent_time = datetime.utcnow() - timedelta(minutes=1)
                recent_articles = await self.get_articles(
                    db=db,
                    since=recent_time,
                    limit=total_new
                )
                
                # Send webhook notification
                if recent_articles:
                    from app.services.webhook_service import webhook_notifier
                    
                    # Convert to dict for webhook
                    articles_data = [
                        {
                            'id': article.id,
                            'title': article.title,
                            'summary': article.summary,
                            'url': article.url,
                            'category': article.category,
                            'published_at': article.published_at.isoformat() if article.published_at else None,
                            'tags': article.tags,
                            'source_id': article.source_id
                        }
                        for article in recent_articles
                    ]
                    
                    await webhook_notifier.send_new_articles(articles_data)
            
            logger.info(f"Total new articles fetched: {total_new}")
            return {
                'total_new': total_new,
                'by_source': results
            }
        
        except Exception as e:
            logger.error(f"Error fetching from all sources: {e}")
            return {'total_new': 0, 'by_source': {}}

