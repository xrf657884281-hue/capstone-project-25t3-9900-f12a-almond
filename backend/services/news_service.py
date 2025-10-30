"""
News API service for fetching real news articles
"""
import requests
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from config import Config
from .news_filter import NewsQualityFilter

logger = logging.getLogger(__name__)

class NewsService:
    """Service for fetching real news from News API"""
    
    def __init__(self):
        self.api_key = Config.NEWS_API_KEY
        self.base_url = Config.NEWS_API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-Key': self.api_key,
            'User-Agent': 'FakeNewsDetectionSystem/1.0'
        })
        self.quality_filter = NewsQualityFilter()
    
    def get_top_headlines(self, 
                         country: str = 'us', 
                         category: Optional[str] = None,
                         sources: Optional[str] = None,
                         q: Optional[str] = None,
                         page_size: int = 20) -> Dict:
        """Get top headlines from News API"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'News API key not configured',
                'articles': []
            }
        
        try:
            params = {
                'country': country,
                'pageSize': page_size
            }
            
            if category:
                params['category'] = category
            if sources:
                params['sources'] = sources
            if q:
                params['q'] = q
            
            response = self.session.get(f"{self.base_url}/top-headlines", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                articles = data.get('articles', [])
                # Filter articles for quality
                filtered_articles = self.quality_filter.filter_articles(articles, min_quality=0.6)
                
                return {
                    'success': True,
                    'total_results': len(filtered_articles),
                    'original_total': data.get('totalResults', 0),
                    'articles': filtered_articles,
                    'source': 'newsapi',
                    'filtered': len(articles) - len(filtered_articles)
                }
            else:
                return {
                    'success': False,
                    'error': f"News API error: {data.get('message', 'Unknown error')}",
                    'articles': []
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"News API request failed: {e}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'articles': []
            }
        except Exception as e:
            logger.error(f"Unexpected error in News API: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'articles': []
            }
    
    def search_news(self, 
                   query: str,
                   language: str = 'en',
                   sort_by: str = 'publishedAt',
                   from_date: Optional[str] = None,
                   to_date: Optional[str] = None,
                   page_size: int = 20) -> Dict:
        """Search for news articles"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'News API key not configured',
                'articles': []
            }
        
        try:
            params = {
                'q': query,
                'language': language,
                'sortBy': sort_by,
                'pageSize': page_size
            }
            
            if from_date:
                params['from'] = from_date
            if to_date:
                params['to'] = to_date
            
            response = self.session.get(f"{self.base_url}/everything", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return {
                    'success': True,
                    'total_results': data.get('totalResults', 0),
                    'articles': data.get('articles', []),
                    'source': 'newsapi'
                }
            else:
                return {
                    'success': False,
                    'error': f"News API error: {data.get('message', 'Unknown error')}",
                    'articles': []
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"News API search failed: {e}")
            return {
                'success': False,
                'error': f"Search failed: {str(e)}",
                'articles': []
            }
        except Exception as e:
            logger.error(f"Unexpected error in News API search: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'articles': []
            }
    
    def get_sources(self, 
                   category: Optional[str] = None,
                   language: str = 'en',
                   country: str = 'us') -> Dict:
        """Get available news sources"""
        if not self.api_key:
            return {
                'success': False,
                'error': 'News API key not configured',
                'sources': []
            }
        
        try:
            params = {
                'language': language,
                'country': country
            }
            
            if category:
                params['category'] = category
            
            response = self.session.get(f"{self.base_url}/sources", params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'ok':
                return {
                    'success': True,
                    'sources': data.get('sources', []),
                    'source': 'newsapi'
                }
            else:
                return {
                    'success': False,
                    'error': f"News API error: {data.get('message', 'Unknown error')}",
                    'sources': []
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"News API sources request failed: {e}")
            return {
                'success': False,
                'error': f"Sources request failed: {str(e)}",
                'sources': []
            }
        except Exception as e:
            logger.error(f"Unexpected error in News API sources: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'sources': []
            }
    
    def format_article_for_detection(self, article: Dict) -> str:
        """Format a news article for fake news detection"""
        title = article.get('title', '')
        description = article.get('description', '')
        content = article.get('content', '')
        source = article.get('source', {}).get('name', 'Unknown')
        published_at = article.get('publishedAt', '')
        
        # Combine title, description, and content
        text_parts = []
        if title:
            text_parts.append(f"Title: {title}")
        if description:
            text_parts.append(f"Description: {description}")
        if content:
            # Remove [Removed] or similar placeholders
            clean_content = content.replace('[Removed]', '').strip()
            if clean_content:
                text_parts.append(f"Content: {clean_content}")
        
        formatted_text = "\n\n".join(text_parts)
        
        # Add metadata
        metadata = f"\n\nSource: {source}"
        if published_at:
            try:
                # Parse and format date
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S UTC')
                metadata += f"\nPublished: {formatted_date}"
            except:
                metadata += f"\nPublished: {published_at}"
        
        return formatted_text + metadata
