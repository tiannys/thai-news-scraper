from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, date, timedelta
from app.database import get_db
from app.schemas import TrendListResponse
from app.services import TrendService

router = APIRouter(prefix="/trends", tags=["trends"])
trend_service = TrendService()


@router.get("/today", response_model=TrendListResponse)
async def get_today_trends(
    limit: int = Query(20, ge=1, le=100, description="Maximum number of trends to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get today's trending keywords
    
    - **limit**: Maximum number of trends to return
    """
    try:
        today = date.today()
        
        # Extract trends if not already done
        await trend_service.extract_trends_for_date(db, today)
        
        # Get trends
        trends = await trend_service.get_trends_for_date(db, today, limit)
        
        return TrendListResponse(
            trends=trends,
            date=datetime.combine(today, datetime.min.time())
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


@router.get("/date/{target_date}", response_model=TrendListResponse)
async def get_trends_by_date(
    target_date: str,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of trends to return"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending keywords for a specific date
    
    - **target_date**: Date in YYYY-MM-DD format
    - **limit**: Maximum number of trends to return
    """
    try:
        # Parse date
        try:
            dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
        
        # Extract trends if not already done
        await trend_service.extract_trends_for_date(db, dt)
        
        # Get trends
        trends = await trend_service.get_trends_for_date(db, dt, limit)
        
        return TrendListResponse(
            trends=trends,
            date=datetime.combine(dt, datetime.min.time())
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")


@router.get("/categories", response_model=dict)
async def get_trending_categories(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of categories"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get trending categories
    
    - **days**: Number of days to analyze
    - **limit**: Maximum number of categories to return
    """
    try:
        since = datetime.utcnow() - timedelta(days=days)
        categories = await trend_service.get_trending_categories(db, since, limit)
        
        return {
            "categories": categories,
            "period_days": days
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending categories: {str(e)}")


@router.get("/sources", response_model=dict)
async def get_top_sources(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of sources"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get most active sources
    
    - **days**: Number of days to analyze
    - **limit**: Maximum number of sources to return
    """
    try:
        since = datetime.utcnow() - timedelta(days=days)
        sources = await trend_service.get_top_sources(db, since, limit)
        
        return {
            "sources": sources,
            "period_days": days
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top sources: {str(e)}")
