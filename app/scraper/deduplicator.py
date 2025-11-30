import hashlib
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class Deduplicator:
    """Content-based deduplication using hashing"""
    
    @staticmethod
    def generate_content_hash(article: Dict) -> str:
        """Generate SHA256 hash from article content"""
        try:
            # Use title + URL as primary deduplication key
            # This handles cases where same article is published with slight variations
            content = f"{article.get('title', '')}|{article.get('url', '')}"
            
            # Create hash
            hash_object = hashlib.sha256(content.encode('utf-8'))
            content_hash = hash_object.hexdigest()
            
            return content_hash
        
        except Exception as e:
            logger.error(f"Error generating content hash: {e}")
            # Fallback to URL-only hash
            return hashlib.sha256(article.get('url', '').encode('utf-8')).hexdigest()
    
    @staticmethod
    def generate_similarity_hash(text: str) -> str:
        """Generate simhash for near-duplicate detection (simplified version)"""
        try:
            # Simplified implementation - in production, use proper simhash library
            # This is a basic word-based hash for demonstration
            
            if not text:
                return ""
            
            # Normalize text
            normalized = text.lower().strip()
            
            # Split into words
            words = normalized.split()
            
            # Create hash from first 50 words (to catch similar articles)
            sample = ' '.join(words[:50])
            
            return hashlib.md5(sample.encode('utf-8')).hexdigest()
        
        except Exception as e:
            logger.error(f"Error generating similarity hash: {e}")
            return ""
    
    def is_duplicate(self, article: Dict, existing_hashes: set) -> bool:
        """Check if article is a duplicate"""
        try:
            content_hash = self.generate_content_hash(article)
            return content_hash in existing_hashes
        
        except Exception as e:
            logger.error(f"Error checking duplicate: {e}")
            return False
    
    def add_hash_to_article(self, article: Dict) -> Dict:
        """Add content hash to article data"""
        article_copy = article.copy()
        article_copy['content_hash'] = self.generate_content_hash(article)
        return article_copy
