from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List
from datetime import datetime


# Source Schemas
class SourceBase(BaseModel):
    name: str
    type: str
    url: str
    category: Optional[str] = None
    country: str = "TH"
    language: str = "th"
    is_active: bool = True
    fetch_interval_minutes: int = 30


class SourceCreate(SourceBase):
    pass


class SourceResponse(SourceBase):
    id: int
    last_fetched_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Article Schemas
class ArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: str
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    published_at: Optional[datetime] = None
    image_url: Optional[str] = None
    language: str = "th"


class ArticleCreate(ArticleBase):
    source_id: int
    content_hash: str


class ArticleResponse(ArticleBase):
    id: int
    source_id: int
    fetched_at: datetime
    created_at: datetime
    source: Optional[SourceResponse] = None
    
    class Config:
        from_attributes = True


class ArticleListResponse(BaseModel):
    articles: List[ArticleResponse]
    total: int
    page: int
    page_size: int


# Trend Schemas
class TrendBase(BaseModel):
    keyword: str
    category: Optional[str] = None
    frequency: int = 1


class TrendResponse(TrendBase):
    id: int
    date: datetime
    article_ids: Optional[List[int]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TrendListResponse(BaseModel):
    trends: List[TrendResponse]
    date: datetime


# Content Idea Schemas
class ContentIdeaBase(BaseModel):
    angle: str
    hook: str
    caption: str
    hashtags: List[str]
    format: str


class ContentIdeaCreate(ContentIdeaBase):
    article_id: int


class ContentIdeaResponse(ContentIdeaBase):
    id: int
    article_id: int
    generated_at: datetime
    used: bool
    performance_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# API Response Schemas
class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    scheduler: str


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
