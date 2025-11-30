from sqlalchemy import Column, Integer, String, Text, Boolean, TIMESTAMP, ARRAY, Float, Date, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base


class Source(Base):
    """News source configuration"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'rss', 'html', 'api'
    url = Column(Text, nullable=False, unique=True)
    category = Column(String(100))  # 'news', 'lifestyle', 'tech', 'entertainment'
    country = Column(String(50), default='TH')
    language = Column(String(10), default='th')
    is_active = Column(Boolean, default=True)
    fetch_interval_minutes = Column(Integer, default=30)
    last_fetched_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    articles = relationship("Article", back_populates="source")


class Article(Base):
    """News article"""
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("sources.id"))
    title = Column(Text, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    url = Column(Text, nullable=False, unique=True)
    author = Column(String(255))
    category = Column(String(100), index=True)
    tags = Column(ARRAY(Text))
    published_at = Column(TIMESTAMP(timezone=True), index=True)
    fetched_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    content_hash = Column(String(64), nullable=False, unique=True, index=True)
    image_url = Column(Text)
    language = Column(String(10), default='th')
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    source = relationship("Source", back_populates="articles")
    content_ideas = relationship("ContentIdea", back_populates="article")


class Trend(Base):
    """Trending keywords and topics"""
    __tablename__ = "trends"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    keyword = Column(String(255), nullable=False)
    category = Column(String(100))
    frequency = Column(Integer, default=1, index=True)
    article_ids = Column(ARRAY(Integer))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())


class ContentIdea(Base):
    """AI-generated content ideas"""
    __tablename__ = "content_ideas"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles.id"))
    angle = Column(Text)
    hook = Column(Text)
    caption = Column(Text)
    hashtags = Column(ARRAY(Text))
    format = Column(String(50))  # 'image', 'carousel', 'reel', 'story'
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    used = Column(Boolean, default=False)
    performance_score = Column(Float)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="content_ideas")
