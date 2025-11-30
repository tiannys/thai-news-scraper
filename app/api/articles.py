from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas import ArticleResponse, ArticleListResponse
from app.services import ArticleService
from app.models import Article

router = APIRouter(prefix="/articles", tags=["articles"])
article_service = ArticleService()


@router.get("/", response_model=ArticleListResponse)
async def get_articles(
    skip: int = Query(0, ge=0, description="Number of articles to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of articles to return"),
    since: Optional[str] = Query(None, description="ISO format datetime, e.g., 2024-01-01T00:00:00"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get articles with optional filters
    
    - **skip**: Pagination offset
    - **limit**: Maximum number of results
    - **since**: Only return articles created after this datetime
    - **category**: Filter by category (news, lifestyle, entertainment, etc.)
    """
    try:
        # Parse since parameter
        since_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid datetime format. Use ISO format.")
        
        # Get articles
        articles = await article_service.get_articles(
            db=db,
            skip=skip,
            limit=limit,
            since=since_dt,
            category=category
        )
        
        # Get total count (simplified - in production, use a separate count query)
        total = len(articles)
        
        return ArticleListResponse(
            articles=articles,
            total=total,
            page=skip // limit + 1,
            page_size=limit
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single article by ID"""
    try:
        article = await article_service.get_article_by_id(db, article_id)
        
        if not article:
            raise HTTPException(status_code=404, detail="Article not found")
        
        return article
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching article: {str(e)}")


@router.post("/fetch", response_model=dict)
async def trigger_fetch(
    db: AsyncSession = Depends(get_db)
):
    """
    Manually trigger article fetching from all sources
    
    This endpoint is useful for testing or forcing an immediate fetch
    """
    try:
        results = await article_service.fetch_from_all_sources(db)
        
        return {
            "status": "success",
            "total_new_articles": results['total_new'],
            "by_source": results['by_source']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching articles: {str(e)}")
