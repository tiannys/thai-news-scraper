# Scraper package initialization
from app.scraper.rss_parser import RSSParser
from app.scraper.normalizer import DataNormalizer
from app.scraper.deduplicator import Deduplicator

__all__ = ['RSSParser', 'DataNormalizer', 'Deduplicator']
