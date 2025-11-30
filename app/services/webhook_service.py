import httpx
import logging
from typing import List, Dict, Optional
from app.config import settings

logger = logging.getLogger(__name__)


class WebhookNotifier:
    """Send notifications to n8n webhook"""
    
    def __init__(self):
        self.webhook_url = settings.webhook_url
        self.webhook_secret = settings.webhook_secret
        self.enabled = settings.webhook_enabled and bool(self.webhook_url)
    
    async def send_new_articles(self, articles: List[Dict]) -> bool:
        """Send new articles to n8n webhook"""
        if not self.enabled:
            logger.debug("Webhook notifications disabled")
            return False
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            # Add secret header if configured
            if self.webhook_secret:
                headers["X-Webhook-Secret"] = self.webhook_secret
            
            # Prepare payload
            payload = {
                "event": "new_articles",
                "timestamp": articles[0].get("created_at") if articles else None,
                "count": len(articles),
                "articles": articles
            }
            
            # Send to webhook
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                logger.info(f"Sent {len(articles)} articles to webhook: {self.webhook_url}")
                return True
        
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending webhook: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending webhook: {e}")
            return False
    
    async def send_trends(self, trends: List[Dict]) -> bool:
        """Send trending topics to n8n webhook"""
        if not self.enabled:
            return False
        
        try:
            headers = {
                "Content-Type": "application/json"
            }
            
            if self.webhook_secret:
                headers["X-Webhook-Secret"] = self.webhook_secret
            
            payload = {
                "event": "new_trends",
                "count": len(trends),
                "trends": trends
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                logger.info(f"Sent {len(trends)} trends to webhook")
                return True
        
        except Exception as e:
            logger.error(f"Error sending trends webhook: {e}")
            return False


# Global webhook notifier instance
webhook_notifier = WebhookNotifier()
