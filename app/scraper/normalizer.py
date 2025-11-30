import re
from typing import Dict
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class DataNormalizer:
    """Normalize and clean article data"""
    
    @staticmethod
    def clean_html(html_text: str) -> str:
        """Remove HTML tags and clean text"""
        if not html_text:
            return ""
        
        try:
            soup = BeautifulSoup(html_text, 'lxml')
            text = soup.get_text(separator=' ', strip=True)
            
            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text)
            
            return text.strip()
        except Exception as e:
            logger.error(f"Error cleaning HTML: {e}")
            return html_text
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL (remove tracking parameters, etc.)"""
        if not url:
            return ""
        
        try:
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            
            parsed = urlparse(url)
            
            # Remove common tracking parameters
            tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'fbclid', 'gclid']
            
            query_params = parse_qs(parsed.query)
            cleaned_params = {k: v for k, v in query_params.items() if k not in tracking_params}
            
            # Rebuild URL
            new_query = urlencode(cleaned_params, doseq=True)
            normalized = urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                ''  # Remove fragment
            ))
            
            return normalized
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            return url
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 500) -> str:
        """Truncate text to max length"""
        if not text or len(text) <= max_length:
            return text
        
        return text[:max_length].rsplit(' ', 1)[0] + '...'
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> list:
        """Extract keywords from text (simple implementation)"""
        if not text:
            return []
        
        try:
            # Remove special characters and convert to lowercase
            cleaned = re.sub(r'[^\u0E00-\u0E7Fa-zA-Z0-9\s]', '', text.lower())
            
            # Split into words
            words = cleaned.split()
            
            # Filter out short words and common Thai stop words
            thai_stopwords = {'ที่', 'และ', 'ใน', 'เป็น', 'ของ', 'มี', 'จาก', 'ได้', 'ว่า', 'ให้', 'แล้ว', 'ไป', 'มา', 'ไม่', 'ก็', 'ถ้า', 'จะ', 'ทั้ง', 'นี้', 'นั้น'}
            filtered_words = [w for w in words if len(w) > 2 and w not in thai_stopwords]
            
            # Count frequency
            from collections import Counter
            word_freq = Counter(filtered_words)
            
            # Get top keywords
            keywords = [word for word, count in word_freq.most_common(max_keywords)]
            
            return keywords
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return []
    
    def normalize_article(self, article: Dict) -> Dict:
        """Normalize all fields in an article"""
        try:
            normalized = article.copy()
            
            # Clean HTML from text fields
            if normalized.get('title'):
                normalized['title'] = self.clean_html(normalized['title'])
            
            if normalized.get('summary'):
                normalized['summary'] = self.clean_html(normalized['summary'])
            
            if normalized.get('content'):
                normalized['content'] = self.clean_html(normalized['content'])
            
            # Normalize URL
            if normalized.get('url'):
                normalized['url'] = self.normalize_url(normalized['url'])
            
            # Ensure summary exists (use content if not)
            if not normalized.get('summary') and normalized.get('content'):
                normalized['summary'] = self.truncate_text(normalized['content'], 500)
            
            # Extract keywords if not present
            if not normalized.get('tags'):
                text = f"{normalized.get('title', '')} {normalized.get('summary', '')}"
                normalized['tags'] = self.extract_keywords(text)
            
            # Clean author name
            if normalized.get('author'):
                normalized['author'] = self.clean_html(normalized['author'])
            
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing article: {e}")
            return article
