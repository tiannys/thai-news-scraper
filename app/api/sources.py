from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.database import get_db
from app.schemas import SourceCreate, SourceResponse
from app.models import Source
import logging

router = APIRouter(prefix="/sources", tags=["sources"])
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[SourceResponse])
async def get_sources(
    db: AsyncSession = Depends(get_db),
    is_active: bool = None
):
    """
    Get all sources
    
    - **is_active**: Filter by active status (optional)
    """
    try:
        query = select(Source)
        
        if is_active is not None:
            query = query.where(Source.is_active == is_active)
        
        query = query.order_by(Source.created_at.desc())
        
        result = await db.execute(query)
        sources = result.scalars().all()
        
        return sources
    
    except Exception as e:
        logger.error(f"Error getting sources: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching sources: {str(e)}")


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a single source by ID"""
    try:
        result = await db.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()
        
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        return source
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching source: {str(e)}")


@router.post("/", response_model=SourceResponse)
async def create_source(
    source: SourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new source
    
    Example request body:
    ```json
    {
        "name": "Oddity Central",
        "type": "rss",
        "url": "https://www.odditycentral.com/feed/",
        "category": "weird",
        "country": "GLOBAL",
        "language": "en",
        "is_active": true,
        "fetch_interval_minutes": 30
    }
    ```
    """
    try:
        # Check if source with same URL already exists
        result = await db.execute(
            select(Source).where(Source.url == source.url)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(
                status_code=400, 
                detail=f"Source with URL '{source.url}' already exists (ID: {existing.id})"
            )
        
        # Create new source
        new_source = Source(**source.model_dump())
        db.add(new_source)
        await db.commit()
        await db.refresh(new_source)
        
        logger.info(f"Created new source: {new_source.name} (ID: {new_source.id})")
        
        return new_source
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating source: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating source: {str(e)}")


@router.patch("/{source_id}/toggle", response_model=SourceResponse)
async def toggle_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Toggle source active status (enable/disable)"""
    try:
        result = await db.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()
        
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        # Toggle active status
        source.is_active = not source.is_active
        await db.commit()
        await db.refresh(source)
        
        status = "enabled" if source.is_active else "disabled"
        logger.info(f"Source {source.name} (ID: {source_id}) {status}")
        
        return source
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error toggling source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error toggling source: {str(e)}")


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a source (use with caution - will affect related articles)"""
    try:
        result = await db.execute(
            select(Source).where(Source.id == source_id)
        )
        source = result.scalar_one_or_none()
        
        if not source:
            raise HTTPException(status_code=404, detail="Source not found")
        
        source_name = source.name
        await db.delete(source)
        await db.commit()
        
        logger.info(f"Deleted source: {source_name} (ID: {source_id})")
        
        return {"status": "success", "message": f"Source '{source_name}' deleted"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting source {source_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting source: {str(e)}")
