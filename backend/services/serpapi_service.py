"""
SerpAPI Service - Google News search using SerpAPI
Provides better news search results than News API free tier
"""
import requests
import logging
from typing import List, Dict, Optional
from config import Config

logger = logging.getLogger(__name__)


class SerpAPIService:
    """Service for fetching news from Google News via SerpAPI"""
    
    def __init__(self):
        self.api_key = Config.SERPAPI_KEY
        self.base_url = Config.SERPAPI_BASE_URL
        self.session = requests.Session()
    
    def search_google_news(
        self, 
        query: str,
        num_results: int = 10,
        time_period: Optional[str] = None,
        use_and_logic: bool = True
    ) -> Dict:

        if not self.api_key:
            return {
                'success': False,
                'error': 'SerpAPI key not configured',
                'articles': []
            }
        
        try:
            # Optimize query for better results
            optimized_query = query
            query_words = query.split()
            
            # Strategy: Keep it simple - only use AND for 2-3 core terms
            # Too many ANDs cause connection failures or no results
            if use_and_logic and len(query_words) > 1:
                if len(query_words) <= 3:
                    # Short phrases: use quotes for exact match
                    optimized_query = f'"{query}"'
                elif len(query_words) <= 5:
                    # 4-5 words: keep all naturally (Google handles it well)
                    optimized_query = query
                else:
                    # 6+ words: Use AND for first 3 ONLY, rest as natural keywords
                    core_terms = ' AND '.join(query_words[:3])
                    extra_terms = ' '.join(query_words[3:6])
                    optimized_query = f"{core_terms} {extra_terms}"
            
            params = {
                'engine': 'google',
                'q': optimized_query,
                'tbm': 'nws',  # News search
                'api_key': self.api_key,
                'num': num_results
            }
            
            if time_period:
                params['tbs'] = time_period
            
            logger.info(f"🔍 SerpAPI search: original='{query}', optimized='{optimized_query}', num={num_results}")
            
            response = self.session.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse SerpAPI response
            news_results = data.get('news_results', [])
            
            if not news_results:
                logger.warning(f"⚠️ No news results from SerpAPI for query: {query}")
                return {
                    'success': True,
                    'total_results': 0,
                    'articles': [],
                    'source': 'serpapi'
                }
            
            # Convert SerpAPI format to our standard format
            articles = []
            for item in news_results[:num_results]:
                article = {
                    'title': item.get('title', ''),
                    'description': item.get('snippet', ''),
                    'url': item.get('link', ''),
                    'source': {
                        'name': item.get('source', {}).get('name', 'Unknown') if isinstance(item.get('source'), dict) else item.get('source', 'Unknown')
                    },
                    'publishedAt': item.get('date', ''),
                    'urlToImage': item.get('thumbnail', ''),
                    'content': item.get('snippet', '')
                }
                articles.append(article)
            
            logger.info(f"✅ SerpAPI returned {len(articles)} news articles")
            
            return {
                'success': True,
                'total_results': len(articles),
                'articles': articles,
                'source': 'serpapi'
            }
            
        except requests.exceptions.Timeout:
            logger.error("❌ SerpAPI request timeout")
            return {
                'success': False,
                'error': 'Request timeout',
                'articles': []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ SerpAPI request failed: {e}")
            return {
                'success': False,
                'error': f"Request failed: {str(e)}",
                'articles': []
            }
        except Exception as e:
            logger.error(f"❌ Unexpected error in SerpAPI: {e}")
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'articles': []
            }
    
    def search_news_by_topic(
        self,
        topic: str,
        num_results: int = 10
    ) -> Dict:

        # Build optimized query
        query = f"{topic} news"
        return self.search_google_news(query, num_results)

