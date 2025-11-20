
import re
import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter
import spacy
from .news_service import NewsService
from .serpapi_service import SerpAPIService
from config import Config

logger = logging.getLogger(__name__)

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np
    SKLEARN_AVAILABLE = True
    logger.info("sklearn available for TF-IDF similarity")
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("sklearn not available, using basic matching")


class RelatedNewsFinder:
    """Find related real news based on detection results"""
    
    def __init__(self):
        self.news_service = NewsService()
        self.serpapi_service = SerpAPIService()
        self.news_cache = {}
        self.cache_ttl = 300
        
        # Determine which service to use
        self.use_serpapi = bool(Config.SERPAPI_KEY)
        if self.use_serpapi:
            logger.info("Using SerpAPI for news search (Google News)")
        else:
            logger.info("SerpAPI key not found, using News API fallback")
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded for news finder")
        except OSError:
            logger.warning("spaCy model not found, using simple keyword extraction")
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
            
            logger.info(f"Extracted {len(unique_entities)} clean entities: {unique_entities}")
            return unique_entities[:10]
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract important keywords from text"""
        # Extended stop words including common but meaningless words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
            # Add common but low-value words
            'new', 'said', 'says', 'over', 'more', 'also', 'very', 'just',
            'about', 'into', 'than', 'some', 'out', 'only', 'other', 'such',
            'get', 'make', 'made', 'like', 'well', 'back', 'after', 'two',
            'three', 'way', 'even', 'year', 'years', 'much', 'any', 'most'
        }
        
        # Extract words 
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stop words and count frequencies
        filtered_words = [w for w in words if w not in stop_words]
        word_freq = Counter(filtered_words)
        
        # Get top keywords by frequency
        top_keywords = [word for word, _ in word_freq.most_common(max_keywords)]
        
        logger.info(f"Extracted {len(top_keywords)} keywords: {top_keywords}")
        return top_keywords
    
    def validate_query_specificity(self, query: str) -> bool:
        """
        Validate if a query is specific enough
        
        Args:
            query: Search query to validate
            
        Returns:
            True if query is specific enough, False if too broad
        """
        # Too broad: single common words
        overly_broad_terms = {
            'trump', 'china', 'australia', 'news', 'today', 'report',
            'study', 'research', 'says', 'new', 'latest', 'update'
        }
        
        words = query.lower().split()
        
        # Reject if single word and it's in broad terms list
        if len(words) == 1 and words[0] in overly_broad_terms:
            logger.warning(f"Query too broad: '{query}' (single common word)")
            return False
        
        # Require at least 2 words for specificity
        if len(words) < 2:
            logger.warning(f"Query too short: '{query}' (need 2+ words)")
            return False
        
        return True
    
    def compute_entity_frequencies(self, text: str, entities: List[str]) -> Dict[str, int]:
        """Count how often each entity occurs in the text (case-insensitive)."""
        frequencies: Dict[str, int] = {}
        lowered_text = text.lower()
        for entity in entities:
            pattern = r'\b' + re.escape(entity.lower()) + r'\b'
            occurrences = len(re.findall(pattern, lowered_text))
            frequencies[entity] = occurrences
        return frequencies
    
    def build_search_query(self, text: str, entities: List[str], keywords: List[str], entity_frequencies: Optional[Dict[str, int]] = None) -> str:
        """
        Build an optimized search query by combining entities and keywords
        
        Strategy: Prioritize multi-word entities (more specific) over single-word entities
        Example: "Eiffel Tower" should come before "China" in query
        """
        query_parts = []
        entity_frequencies = entity_frequencies or {}
        
        # Sort entities by frequency (desc), then by specificity (multi-word before single-word)
        def sort_entities(entity_list: List[str]) -> List[str]:
            return sorted(
                entity_list,
                key=lambda e: (
                    entity_frequencies.get(e, 0),
                    len(e.split()) > 1,
                    len(e)
                ),
                reverse=True
            )
        
        high_frequency_entities = [e for e in entities if entity_frequencies.get(e, 0) >= 2]
        low_frequency_entities = [e for e in entities if entity_frequencies.get(e, 0) < 2]
        ordered_entities = sort_entities(high_frequency_entities) + sort_entities(low_frequency_entities)
        
        multi_word_entities = [e for e in ordered_entities if len(e.split()) > 1 and len(e.split()) <= 3]
        single_word_entities = [e for e in ordered_entities if len(e.split()) == 1]
        
        # Step 1: Add up to two multi-word entities (already frequency-sorted)
        if multi_word_entities:
            query_parts.extend(multi_word_entities[:2])
        
        # Step 2: Add relevant keywords that aren't in entities
        entities_lower = [e.lower() for e in entities]
        unique_keywords = []
        for kw in keywords[:5]:
            # Skip if keyword is already part of an entity
            if kw not in entities_lower:
                unique_keywords.append(kw)
        
        # Add top 2-3 unique keywords
        query_parts.extend(unique_keywords[:3])
        
        # Step 3: Add single-word entities if we still need more terms
        if len(query_parts) < 4:
            query_parts.extend(single_word_entities[:2])
        
        # Remove duplicates while preserving order
        seen = set()
        final_parts = []
        for part in query_parts:
            part_lower = part.lower()
            if part_lower not in seen:
                seen.add(part_lower)
                final_parts.append(part)
        
        # Build final query (limit to 6-7 words for best results)
        query = ' '.join(final_parts[:7])
        
        # Validate specificity
        if not self.validate_query_specificity(query):
            # If still not specific enough, add context from text
            context_words = [w for w in text.split()[:15] if len(w) > 4]
            query = f"{query} {' '.join(context_words[:2])}"
        
        logger.info(f"Search query (combined): {query}")
        logger.info(
            "   Components: %d multi-word entities + %d keywords + %d single entities (freq-aware)",
            len(multi_word_entities), len(unique_keywords), len(single_word_entities)
        )
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
            logger.info(f"Finding related news for text (length: {len(text)})")
            
            # Check cache first
            import time
            cache_key = text[:100]  # Use first 100 chars as key
            if cache_key in self.news_cache:
                cached_time, cached_result = self.news_cache[cache_key]
                if time.time() - cached_time < self.cache_ttl:
                    logger.info(f"Using cached result (age: {int(time.time() - cached_time)}s)")
                    return cached_result
        
            entities = []
            keywords = []
            
            # Priority 1: Use Tavily verified entities (most reliable)
            if detection_result:
                tavily_verification = detection_result.get('tavily_verification', {})
                entity_results = tavily_verification.get('entity_results', [])
                
                if entity_results:
                    # Extract entities from Tavily, with strict cleaning
                    tavily_entities = []
                    for e in entity_results:
                        entity_name = e.get('entity', '').strip()
                        if entity_name:
                            # Skip pure numeric entities (years, numbers)
                            if entity_name.isdigit():
                                logger.info(f"Skipping numeric entity: {entity_name}")
                                continue
                            
                            # Skip very short entities (< 3 chars)
                            if len(entity_name) < 3:
                                continue
                            
                            # Clean entity: remove newlines, extra spaces, trailing punctuation
                            entity_name = ' '.join(entity_name.split())  # Remove all extra whitespace/newlines
                            entity_name = entity_name.rstrip('.,;:-')  # Remove trailing punctuation
                            
                            # Skip if contains newlines or strange characters
                            if '\n' in entity_name or '\r' in entity_name:
                                logger.info(f"Skipping malformed entity: {entity_name[:30]}...")
                                continue
                            
                            # Skip very long entities (> 50 chars, likely extraction errors)
                            if len(entity_name) > 50:
                                logger.info(f"Skipping too long entity: {entity_name[:30]}...")
                                continue
                            
                            # Only keep if it has some alphabetic characters
                            if any(c.isalpha() for c in entity_name):
                                tavily_entities.append(entity_name)
                    
                    # Prioritize entities that were verified (exists=True)
                    verified_entities = []
                    for e in entity_results:
                        if e.get('exists') and e.get('entity'):
                            entity_name = e.get('entity', '').strip()
                            # Clean and validate
                            entity_name = ' '.join(entity_name.split())  # Remove newlines/extra spaces
                            entity_name = entity_name.rstrip('.,;:-')
                            
                            # Skip if numeric, too short, or has newlines
                            if (not entity_name.isdigit() and 
                                len(entity_name) >= 3 and
                                '\n' not in entity_name and 
                                len(entity_name) <= 50):
                                verified_entities.append(entity_name)
                    
                    if verified_entities:
                        entities = verified_entities
                        logger.info(f" Using {len(verified_entities)} Tavily verified entities: {verified_entities}")
                    elif tavily_entities:
                        entities = tavily_entities
                        logger.info(f" Using {len(tavily_entities)} Tavily entities (unverified): {tavily_entities}")
            
            # Priority 2: If no Tavily entities, extract from text
            if not entities:
                logger.info("No Tavily entities available, extracting from text...")
                entities = self.extract_entities(text)
            
            # Always extract keywords as backup
            keywords = self.extract_keywords(text)
            
            # Remove duplicates while preserving order
            entities = list(dict.fromkeys(entities))

            entity_frequencies = self.compute_entity_frequencies(text, entities)

            search_query = self.build_search_query(text, entities, keywords, entity_frequencies)
            
           
            year = self.extract_date_context(text)
            from_date = None
            if year:
                try:
                    year_int = int(year)
                    if 2000 <= year_int <= 2025:  
                        from_date = f"{year_int}-01-01"
                        logger.info(f"Temporal filter: from {from_date}")
                except:
                    pass
            
            # Step 6: Search for news
            # Use SerpAPI if available (better results), otherwise fallback to News API
            if self.use_serpapi:
                logger.info(f"Using SerpAPI (Google News) to search: {search_query}")
                news_result = self.serpapi_service.search_google_news(
                    query=search_query,
                    num_results=max_results * 2  # Get more for ranking
                )
            else:
                logger.info(f"Using News API to search: {search_query}")
                news_result = self.news_service.search_news(
                    query=search_query,
                    language=language,
                    page_size=max_results,
                    from_date=from_date
                )
            
            # If search succeeded, rank the results
            if news_result.get('success') and news_result.get('articles'):
                initial_articles = news_result.get('articles', [])
                logger.info(f"Initial search returned {len(initial_articles)} articles, ranking...")
                ranked = self.rank_articles_by_relevance(initial_articles, entities, keywords, text)
                news_result['articles'] = ranked[:max_results]  # Limit to requested number
            
            # Fallback to top headlines if search fails 
            if not news_result.get('success') or not news_result.get('articles'):
                logger.info(f"Search API failed, trying top headlines with query: {search_query[:40]}...")
                
                all_articles = []
                
                # Use country + query 
                countries = ['us', 'gb', 'au', 'ca']
                
                for country in countries:
                    if len(all_articles) >= max_results * 2:
                        break
                    
                    logger.info(f"Searching {country.upper()} headlines with query: {search_query[:30]}...")
                    
                    # Use top headlines WITH query parameter
                    news_result = self.news_service.get_top_headlines(
                        country=country,
                        q=search_query,
                        page_size=max_results
                    )
                    
                    if news_result.get('success') and news_result.get('articles'):
                        articles_found = news_result.get('articles', [])
                        all_articles.extend(articles_found)
                        logger.info(f"Got {len(articles_found)} relevant articles from {country.upper()}")
                
                # If still no results with query, try category-based search
                if len(all_articles) == 0 and entities:
                    logger.info(f"No results with query, trying category-based search for entities: {entities[:2]}")
                    
                    # Try different categories based on context
                    categories = ['science', 'technology', 'general']
                    
                    for category in categories:
                        if len(all_articles) >= max_results:
                            break
                        
                        for country in ['us', 'gb']:
                            news_result = self.news_service.get_top_headlines(
                                country=country,
                                category=category,
                                page_size=max_results
                            )
                            if news_result.get('success') and news_result.get('articles'):
                                all_articles.extend(news_result.get('articles', []))
                                logger.info(f"Got {len(news_result.get('articles', []))} {category} articles from {country.upper()}")
                                if len(all_articles) >= max_results * 2:  # Get extra for ranking
                                    break
                        
                        if len(all_articles) >= max_results * 2:
                            break
                
                if all_articles:
                    logger.info(f"Fallback successful: {len(all_articles)} articles collected")
                    # Rank by relevance using TF-IDF and word boundary matching
                    ranked_articles = self.rank_articles_by_relevance(all_articles, entities, keywords, text)
                    
                    # Return top articles sorted by relevance score (no threshold)
                    # This ensures users always see results, even if relevance is low
                    if ranked_articles:
                        top_articles = ranked_articles[:max_results]
                        max_score = max(a.get('relevance_score', 0) for a in top_articles)
                        avg_score = sum(a.get('relevance_score', 0) for a in top_articles) / len(top_articles)
                        
                        logger.info(f"Returning {len(top_articles)} articles sorted by relevance")
                        logger.info(f"   Scores: max={max_score:.1f}, avg={avg_score:.1f}")
                        
                        news_result = {
                            'success': True,
                            'articles': top_articles,
                            'total_results': len(all_articles),
                            'max_score': max_score,
                            'avg_score': avg_score
                        }
                    else:
                        logger.warning(f"⚠️ No articles found")
                        news_result = {
                            'success': True,
                            'articles': [],
                            'total_results': 0,
                            'warning': 'No news articles found for this topic'
                        }
                else:
                    news_result = {
                        'success': False,
                        'error': 'No articles found',
                        'articles': []
                    }
            
            if news_result.get('success'):
                articles = news_result.get('articles', [])
                logger.info(f"Found {len(articles)} related news articles")
                
                # If we got very few results and we used entities, try keywords as well
                if len(articles) < max_results and entities and keywords:
                    logger.info(f"Only {len(articles)} articles found with entities, supplementing with more articles...")
                    
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
                        
                        logger.info(f"Re-ranked {len(all_combined)} articles, selected top {len(articles)}")
                
                final_result = {
                    'success': True,
                    'articles': articles[:max_results],
                    'total_results': len(articles),
                    'search_query': search_query,
                    'entities_used': entities[:3],
                    'keywords_used': keywords[:5],
                    'source': 'newsapi'
                }
                
                # Store in cache
                import time
                self.news_cache[cache_key] = (time.time(), final_result)
                logger.info(f"Cached result for future requests")
                
                return final_result
            else:
                error_msg = news_result.get('error', 'Unknown error')
                logger.error(f"News search failed: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg,
                    'articles': []
                }
                
        except Exception as e:
            logger.error(f"Related news finder error: {e}", exc_info=True)
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
                
                logger.info(f"TF-IDF similarity calculated for {len(articles)} articles")
            except Exception as e:
                logger.warning(f"TF-IDF calculation failed: {e}")
        
        # Debug logging
        logger.info(f"🔍 Ranking {len(articles)} articles with:")
        logger.info(f"   Entities: {entities[:5]}")
        logger.info(f"   Keywords: {keywords[:5]}")
        
        # Separate multi-word and single-word entities
        multi_word_entities = [e for e in entities if len(e.split()) > 1]
        single_word_entities = [e for e in entities if len(e.split()) == 1]
        
        # Score each article
        for idx, article in enumerate(articles):
            score = 0
            title = (article.get('title', '') or '')
            description = (article.get('description', '') or '')
            content = (article.get('content', '') or '')
            
            combined_text = f"{title} {description} {content}"
            combined_lower = combined_text.lower()
            
            # Method 1: Regex word boundary matching (precise matching)
            entity_score = 0
            keyword_score = 0
            multi_word_matches = 0
            
            # Prioritize multi-word entities (much higher weight, e.g., "Eiffel Tower")
            for entity in multi_word_entities:
                pattern = r'\b' + re.escape(entity.lower()) + r'\b'
                matches = len(re.findall(pattern, combined_lower))
                if matches > 0:
                    multi_word_matches += 1
                    entity_score += matches * 15  # Much higher weight for multi-word entities
                    logger.info(f"Multi-word entity match: '{entity}' x{matches} in article {idx+1}")
            
            # Score single-word entities (lower weight, e.g., "China")
            for entity in single_word_entities:
                pattern = r'\b' + re.escape(entity.lower()) + r'\b'
                matches = len(re.findall(pattern, combined_lower))
                if matches > 0:
                    entity_score += matches * 3  # Lower weight for single-word entities
                    logger.info(f"Single-word entity match: '{entity}' x{matches} in article {idx+1}")
            
            # Score by keyword matches with word boundaries
            for keyword in keywords:
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                matches = len(re.findall(pattern, combined_lower))
                if matches > 0:
                    keyword_score += matches * 2  # Medium weight for keywords
                    logger.info(f"Keyword match: '{keyword}' x{matches} in article {idx+1}")
            
            # Bonus: If article matches multi-word entities, boost score significantly
            if multi_word_matches > 0:
                score = entity_score + keyword_score + (multi_word_matches * 10)  # Bonus for matching main entities
            else:
                # Penalty: If no multi-word entities matched but they exist, reduce score
                if multi_word_entities:
                    score = (entity_score + keyword_score) * 0.3  # Heavy penalty
                else:
                    score = entity_score + keyword_score
            
            # Method 2: Add TF-IDF similarity score (if available)
            if idx in tfidf_scores:
                tfidf_score = tfidf_scores[idx]
                score += tfidf_score * 20  
                article['tfidf_similarity'] = round(tfidf_score, 3)
            
            article['relevance_score'] = score
            scored_articles.append(article)
        
        # Sort by relevance score (descending)
        ranked = sorted(scored_articles, key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"Ranked {len(ranked)} articles by relevance (TF-IDF: {SKLEARN_AVAILABLE})")
        if ranked:
            top_scores = [a.get('relevance_score', 0) for a in ranked[:3]]
            logger.info(f" only top 3 scores: {top_scores}")
        
        return ranked


# Global instance
related_news_finder = RelatedNewsFinder()


def find_related_news(text: str, detection_result: Optional[Dict] = None, max_results: int = 4) -> Dict:

    return related_news_finder.find_related_news(text, detection_result, max_results)

