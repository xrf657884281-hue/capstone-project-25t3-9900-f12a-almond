
import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter
import spacy
from .news_service import NewsService

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
    logger.info("✅ sklearn available for TF-IDF similarity")
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("⚠️ sklearn not available, using basic matching")


class RelatedNewsFinder:
    """Find related real news based on detection results"""
    
    def __init__(self):
        self.news_service = NewsService()
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded for news finder")
        except OSError:
            logger.warning("⚠️ spaCy model not found, using simple keyword extraction")
            self.nlp = None
    
    def extract_entities(self, text: str) -> List[str]:
       
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text[:1000])
            
            # Noise words that shouldn't appear in valid entities should be removed
            noise_words = {'with', 'from', 'to', 'for', 'by', 'at', 'in', 'on', 'of', 
                          'and', 'or', 'but', 'the', 'a', 'an', 'power', 'has', 'have'}
            
            # Common verbs that indicate invalid entity extraction
            verb_indicators = {'power', 'has', 'have', 'is', 'are', 'was', 'were', 'be'}
            
            entities = []
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'LOC', 'PRODUCT']:
                    entity_text = ent.text.strip()
                    words = entity_text.split()
                    
                    # Skip if too long (> 3 words for better precision)
                    if len(words) > 3:
                        continue
                    
                    # Skip if first or last word is a noise word
                    words_lower = [w.lower() for w in words]
                    if words_lower and (words_lower[0] in noise_words or words_lower[-1] in noise_words):
                        continue
                    
                    # Skip if contains verb indicators
                    if any(w in verb_indicators for w in words_lower):
                        continue
                    
                    # Skip entities starting with lowercase (likely extraction errors)
                    if entity_text and not entity_text[0].isupper():
                        continue
                    
                    # Only keep clean entities (alphabetic + spaces/hyphens)
                    if entity_text and 2 <= len(entity_text) <= 40:
                        clean_text = entity_text.replace(' ', '').replace('-', '')
                        if clean_text.isalpha():
                            entities.append(entity_text)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_entities = []
            for e in entities:
                e_lower = e.lower()
                if e_lower not in seen:
                    seen.add(e_lower)
                    unique_entities.append(e)
            
            logger.info(f"📝 Extracted {len(unique_entities)} clean entities: {unique_entities}")
            return unique_entities[:10]
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract important keywords from text"""
        # Common stop words to filter out
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their'
        }
        
        # Extract words 
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stop words and count frequencies
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Get top keywords by frequency
        top_keywords = [word for word, _ in word_freq.most_common(max_keywords)]
        
        logger.info(f"📝 Extracted {len(top_keywords)} keywords: {top_keywords}")
        return top_keywords
    
    def build_search_query(self, text: str, entities: List[str], keywords: List[str]) -> str:
        """Build an optimized search query from entities and keywords"""
        # Use entities (most relevant)
        if entities:
           
            query_parts = entities[:3]
            query = ' '.join(query_parts)
            logger.info(f"🔍 Search query (entities): {query}")
            return query
        
      
        if keywords:
            query = ' '.join(keywords[:5])
            logger.info(f"🔍 Search query (keywords): {query}")
            return query
        
       
        words = text.split()[:10]
        query = ' '.join(words)
        logger.info(f"🔍 Search query (fallback): {query}")
        return query
    
    def extract_date_context(self, text: str) -> Optional[str]:
        """Extract year/date mentions from text for temporal filtering"""
      
        years = re.findall(r'\b(20\d{2}|19\d{2})\b', text)
        if years:
            
            return max(years)
        return None
    
    def find_related_news(
        self, 
        text: str, 
        detection_result: Optional[Dict] = None,
        max_results: int = 4,
        language: str = 'en'
    ) -> Dict:

        try:
            logger.info(f"🔍 Finding related news for text (length: {len(text)})")
       
            entities = self.extract_entities(text)
           
            keywords = self.extract_keywords(text)
            
            
            if detection_result:
                # Extract entities from tavily verification if available
                tavily_verification = detection_result.get('tavily_verification', {})
                entity_results = tavily_verification.get('entity_results', [])
                
                if entity_results:
                    # Add verified entities to search
                    verified_entities = [
                        e.get('entity') for e in entity_results 
                        if e.get('exists') and e.get('entity')
                    ]
                    entities.extend(verified_entities)
                    logger.info(f"📝 Added {len(verified_entities)} verified entities from detection")
            
        
            entities = list(dict.fromkeys(entities))

            search_query = self.build_search_query(text, entities, keywords)
            
           
            year = self.extract_date_context(text)
            from_date = None
            if year:
                try:
                    year_int = int(year)
                    if 2000 <= year_int <= 2025:  
                        from_date = f"{year_int}-01-01"
                        logger.info(f"📅 Temporal filter: from {from_date}")
                except:
                    pass
            
            # Step 6: Search for news

            news_result = self.news_service.search_news(
                query=search_query,
                language=language,
                page_size=max_results,
                from_date=from_date
            )
            
            # Fallback to top headlines if search fails 
            if not news_result.get('success') or not news_result.get('articles'):
                logger.info("⚠️ Search API failed (free tier limitation), trying global top headlines...")
                
                # Use international news sources for global coverage
                global_sources = [
                    'bbc-news',           # BBC (UK)
                    'cnn',                # CNN (US)
                    'reuters',            # Reuters (Global)
                    'al-jazeera-english', # Al Jazeera (Middle East)
                    'the-guardian-uk',    # The Guardian (UK)
                    'abc-news-au',        # ABC (Australia)
                    'cbc-news',           # CBC (Canada)
                ]
                
                all_articles = []
                

                for source_batch in [global_sources[:3], global_sources[3:]]:
                    sources_str = ','.join(source_batch)
                    logger.info(f"🌍 Trying sources: {sources_str}")
                    
                    try:
                        # Call News API directly without country parameter
                        import requests
                        response = requests.get(
                            f"{self.news_service.base_url}/top-headlines",
                            params={
                                'sources': sources_str,
                                'pageSize': max_results
                            },
                            headers={'X-API-Key': self.news_service.api_key}
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('status') == 'ok':
                                articles = data.get('articles', [])
                                all_articles.extend(articles)
                                logger.info(f"✅ Got {len(articles)} articles from global sources")
                        else:
                            logger.warning(f"⚠️ Sources request failed: {response.status_code}")
                    except Exception as e:
                        logger.warning(f"⚠️ Source batch failed: {e}")
                    
                    if len(all_articles) >= max_results:
                        break
                
                # If still no results, try by regions
                if len(all_articles) < max_results:
                    logger.info("🌍 Trying regional headlines...")
                    regions = ['us', 'gb', 'au', 'ca', 'de', 'fr', 'jp', 'cn']  
                    
                    for country in regions:
                        if len(all_articles) >= max_results:
                            break
                        
                        news_result = self.news_service.get_top_headlines(
                            country=country,
                            page_size=2 
                        )
                        
                        if news_result.get('success') and news_result.get('articles'):
                            all_articles.extend(news_result.get('articles', []))
                            logger.info(f"✅ Got articles from {country.upper()}")
                
                if all_articles:
                    logger.info(f"✅ Global fallback successful: {len(all_articles)} articles from worldwide sources")
                    # Rank articles by relevance using TF-IDF and word boundary matching
                    ranked_articles = self.rank_articles_by_relevance(all_articles, entities, keywords, text)
                    news_result = {
                        'success': True,
                        'articles': ranked_articles[:max_results],
                        'total_results': len(all_articles)
                    }
                else:
                    news_result = {
                        'success': False,
                        'error': 'No articles found from global sources',
                        'articles': []
                    }
            
            if news_result.get('success'):
                articles = news_result.get('articles', [])
                logger.info(f"✅ Found {len(articles)} related news articles")
                
                # If we got very few results and we used entities, try keywords as well
                if len(articles) < max_results and entities and keywords:
                    logger.info(f"⚠️ Only {len(articles)} articles found with entities, supplementing with more articles...")
                    
                    # Get more general articles
                    supplement_result = self.news_service.get_top_headlines(
                        country='us',
                        page_size=max_results * 2  # Get more to rank
                    )
                    
                    if supplement_result.get('success') and supplement_result.get('articles'):
                        supplement_articles = supplement_result.get('articles', [])
                        
                        # Remove duplicates
                        existing_urls = {a.get('url') for a in articles if a.get('url')}
                        unique_supplements = [a for a in supplement_articles if a.get('url') not in existing_urls]
                        
                        # Combine and rank all articles using TF-IDF
                        all_combined = articles + unique_supplements
                        ranked_combined = self.rank_articles_by_relevance(all_combined, entities, keywords, text)
                        articles = ranked_combined[:max_results]
                        
                        logger.info(f"✅ Re-ranked {len(all_combined)} articles, selected top {len(articles)}")
                
                return {
                    'success': True,
                    'articles': articles[:max_results],
                    'total_results': len(articles),
                    'search_query': search_query,
                    'entities_used': entities[:3],
                    'keywords_used': keywords[:5],
                    'source': 'newsapi'
                }
            else:
                error_msg = news_result.get('error', 'Unknown error')
                logger.error(f"❌ News search failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'articles': []
                }
                
        except Exception as e:
            logger.error(f"❌ Related news finder error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'articles': []
            }
    
    def find_news_by_entities(
        self,
        entities: List[str],
        max_results: int = 4,
        language: str = 'en'
    ) -> Dict:
        """
        Find news articles by specific entities
        
        Args:
            entities: List of entity names to search for
            max_results: Maximum number of articles
            language: Language code
            
        Returns:
            Dict with news articles
        """
        if not entities:
            return {
                'success': False,
                'error': 'No entities provided',
                'articles': []
            }
        
        # Build query from entities
        query = ' '.join(entities[:3]) 
        
        logger.info(f"🔍 Searching news by entities: {query}")
        
        return self.news_service.search_news(
            query=query,
            language=language,
            page_size=max_results
        )
    
    def rank_articles_by_relevance(
        self,
        articles: List[Dict],
        entities: List[str],
        keywords: List[str],
        source_text: str = ""
    ) -> List[Dict]:

        if not articles:
            return []
        
        scored_articles = []
        
        # Method 2: TF-IDF Cosine Similarity (if sklearn available)
        tfidf_scores = {}
        if SKLEARN_AVAILABLE and source_text:
            try:
                # Prepare documents
                article_texts = []
                for article in articles:
                    title = article.get('title', '') or ''
                    description = article.get('description', '') or ''
                    content = article.get('content', '') or ''
                    article_text = f"{title} {description} {content}"
                    article_texts.append(article_text)
                
                # Calculate TF-IDF
                all_texts = [source_text[:500]] + article_texts
                vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
                tfidf_matrix = vectorizer.fit_transform(all_texts)
                
                # Calculate cosine similarity with source text
                source_vector = tfidf_matrix[0:1]
                article_vectors = tfidf_matrix[1:]
                similarities = cosine_similarity(source_vector, article_vectors)[0]
                
                for i, sim in enumerate(similarities):
                    tfidf_scores[i] = float(sim)
                
                logger.info(f"📊 TF-IDF similarity calculated for {len(articles)} articles")
            except Exception as e:
                logger.warning(f"⚠️ TF-IDF calculation failed: {e}")
        
        # Score each article
        for idx, article in enumerate(articles):
            score = 0
            title = (article.get('title', '') or '')
            description = (article.get('description', '') or '')
            content = (article.get('content', '') or '')
            
            combined_text = f"{title} {description} {content}"
            combined_lower = combined_text.lower()
            
            # Method 1: Regex word boundary matching (precise matching)
            # Score by entity matches with word boundaries (higher weight)
            for entity in entities:
                # Use \b for word boundary to avoid partial matches
                pattern = r'\b' + re.escape(entity.lower()) + r'\b'
                matches = len(re.findall(pattern, combined_lower))
                if matches > 0:
                    score += matches * 5  # Higher weight for entities
            
            # Score by keyword matches with word boundaries
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, combined_lower))
                if matches > 0:
                    score += matches * 2  # Medium weight for keywords
            
            # Method 2: Add TF-IDF similarity score (if available)
            if idx in tfidf_scores:
                tfidf_score = tfidf_scores[idx]
                score += tfidf_score * 20  # Scale TF-IDF (0-1) to comparable range
                article['tfidf_similarity'] = round(tfidf_score, 3)
            
            article['relevance_score'] = score
            scored_articles.append(article)
        
        # Sort by relevance score (descending)
        ranked = sorted(scored_articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"📊 Ranked {len(ranked)} articles by relevance (TF-IDF: {SKLEARN_AVAILABLE})")
        if ranked:
            top_scores = [a.get('relevance_score', 0) for a in ranked[:3]]
            logger.info(f"📈 Top 3 scores: {top_scores}")
        
        return ranked


# Global instance
related_news_finder = RelatedNewsFinder()


def find_related_news(text: str, detection_result: Optional[Dict] = None, max_results: int = 4) -> Dict:

    return related_news_finder.find_related_news(text, detection_result, max_results)

