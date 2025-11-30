# API package initialization
from app.api.articles import router as articles_router
from app.api.trends import router as trends_router

__all__ = ['articles_router', 'trends_router']
