import feedparser
import httpx
from urllib.robotparser import RobotFileParser
from typing import List, Dict, Optional
from datetime import datetime
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class RSSParser:
    """RSS feed parser with robots.txt compliance"""
    
    def __init__(self):
        self.user_agent = settings.scraper_user_agent
        self.timeout = settings.scraper_timeout
        self.respect_robots = settings.scraper_respect_robots_txt
        self.robots_cache = {}
    
    async def check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt"""
        if not self.respect_robots:
            return True
        
        try:
            # Extract base URL
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            robots_url = f"{base_url}/robots.txt"
            
            # Check cache
            if robots_url in self.robots_cache:
                rp = self.robots_cache[robots_url]
            else:
                # Fetch and parse robots.txt
                rp = RobotFileParser()
                rp.set_url(robots_url)
                
                async with httpx.AsyncClient() as client:
                    try:
                        response = await client.get(
                            robots_url,
                            timeout=10,
                            headers={"User-Agent": self.user_agent}
                        )
                        if response.status_code == 200:
                            rp.parse(response.text.splitlines())
                            self.robots_cache[robots_url] = rp
                        else:
                            # If robots.txt not found, assume allowed
                            return True
                    except Exception as e:
                        logger.warning(f"Could not fetch robots.txt from {robots_url}: {e}")
                        return True
            
            # Check if URL is allowed
            return rp.can_fetch(self.user_agent, url)
        
        except Exception as e:
            logger.error(f"Error checking robots.txt for {url}: {e}")
            return False
    
    async def fetch_feed(self, url: str) -> Optional[feedparser.FeedParserDict]:
        """Fetch and parse RSS feed"""
        try:
            # Check robots.txt
            if not await self.check_robots_txt(url):
                logger.warning(f"URL {url} is disallowed by robots.txt")
                return None
            
            # Fetch feed
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    timeout=self.timeout,
                    headers={
                        "User-Agent": self.user_agent,
                        "Accept": "application/rss+xml, application/xml, text/xml"
                    },
                    follow_redirects=True
                )
                response.raise_for_status()
                
                # Parse feed
                feed = feedparser.parse(response.content)
                
                if feed.bozo:
                    logger.warning(f"Feed {url} has parsing errors: {feed.bozo_exception}")
                
                return feed
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching feed {url}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching feed {url}: {e}")
            return None
    
    def parse_entry(self, entry: Dict, source_id: int, category: str) -> Dict:
        """Parse a single feed entry into article data"""
        try:
            # Extract published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                from time import mktime
                published_at = datetime.fromtimestamp(mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                from time import mktime
                published_at = datetime.fromtimestamp(mktime(entry.updated_parsed))
            
            # Extract summary/description
            summary = None
            if hasattr(entry, 'summary'):
                summary = entry.summary
            elif hasattr(entry, 'description'):
                summary = entry.description
            
            # Extract content
            content = None
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value
            
            # Extract image
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.get('type', '').startswith('image/'):
                        image_url = enclosure.get('href')
                        break
            
            # Extract tags
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
            
            # Extract author
            author = None
            if hasattr(entry, 'author'):
                author = entry.author
            
            return {
                'source_id': source_id,
                'title': entry.title if hasattr(entry, 'title') else 'Untitled',
                'summary': summary,
                'content': content,
                'url': entry.link if hasattr(entry, 'link') else '',
                'author': author,
                'category': category,
                'tags': tags,
                'published_at': published_at,
                'image_url': image_url,
                'language': 'th'
            }
        
        except Exception as e:
            logger.error(f"Error parsing entry: {e}")
            return None
    
    async def parse_feed(self, url: str, source_id: int, category: str) -> List[Dict]:
        """Fetch and parse all entries from a feed"""
        feed = await self.fetch_feed(url)
        
        if not feed or not hasattr(feed, 'entries'):
            return []
        
        articles = []
        for entry in feed.entries:
            article_data = self.parse_entry(entry, source_id, category)
            if article_data and article_data['url']:
                articles.append(article_data)
        
        logger.info(f"Parsed {len(articles)} articles from {url}")
        return articles
