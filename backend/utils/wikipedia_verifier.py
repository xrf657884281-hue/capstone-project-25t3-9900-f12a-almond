import requests
import re
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class WikipediaVerifier:
    def __init__(self):
        self.api_url = "https://en.wikipedia.org/w/api.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'FakeNewsDetectionSystem/1.0 (Educational Purpose; https://github.com/fakenews-detection) Python/requests'
        })
        # Increase cache size and timeout settings
        self.cache = {}
        self.cache_size_limit = 1000  # Limit cache size
        self.timeout = 5  # Reduce timeout
        
    def search_wikipedia(self, query: str, limit: int = 5) -> List[Dict]:
        """Search Wikipedia pages"""
        cache_key = f"{query}_{limit}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        params = {
            'action': 'query',
            'list': 'search',
            'srsearch': query,
            'format': 'json',
            'srlimit': limit,
            'srprop': 'snippet|timestamp'
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'query' in data and 'search' in data['query']:
                for item in data['query']['search']:
                    results.append({
                        'title': item['title'],
                        'snippet': self._clean_html(item['snippet']),
                        'timestamp': item.get('timestamp', '')
                    })
            
            # Manage cache size
            if len(self.cache) >= self.cache_size_limit:
                # Remove oldest cache entry
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = results
            return results
        except Exception as e:
            logger.error(f"Wikipedia search failed for query '{query}': {e}")
            return []
    
    def get_page_content(self, title: str) -> Optional[str]:
        """Get Wikipedia page content"""
        cache_key = f"content_{title}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        params = {
            'action': 'query',
            'format': 'json',
            'titles': title,
            'prop': 'extracts',
            'exintro': True,
            'explaintext': True
        }
        
        try:
            response = self.session.get(self.api_url, params=params, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
            
            pages = data.get('query', {}).get('pages', {})
            for page_id, page_data in pages.items():
                if page_id != '-1' and 'extract' in page_data:
                    content = page_data['extract']
                    self.cache[cache_key] = content
                    return content
            
            return None
        except Exception as e:
            logger.error(f"Failed to get Wikipedia content for '{title}': {e}")
            return None
    
    def verify_entity(self, entity: str) -> Dict:
        """Verify if entity exists in Wikipedia"""
        results = self.search_wikipedia(entity, limit=3)
        
        if not results:
            return {
                'entity': entity,
                'found': False,
                'confidence': 0.0,
                'sources': []
            }
        
        # Check title match score
        best_match = None
        best_score = 0.0
        
        for result in results:
            title = result['title'].lower()
            entity_lower = entity.lower()
            
            # Calculate match score
            if title == entity_lower:
                score = 1.0
            elif entity_lower in title or title in entity_lower:
                score = 0.8
            else:
                score = 0.5
            
            if score > best_score:
                best_score = score
                best_match = result
        
        return {
            'entity': entity,
            'found': best_score > 0.5,
            'confidence': best_score,
            'sources': results[:2] if best_match else []
        }
    
    def verify_claim(self, claim: str) -> Dict:
        """Verify if claim is supported in Wikipedia"""
        # Extract keywords for search
        keywords = self._extract_keywords(claim)
        if not keywords:
            return {
                'claim': claim,
                'verified': False,
                'confidence': 0.0,
                'sources': []
            }
        
        # Search related pages
        search_query = ' '.join(keywords[:3])  # Use first 3 keywords
        results = self.search_wikipedia(search_query, limit=5)
        
        if not results:
            return {
                'claim': claim,
                'verified': False,
                'confidence': 0.0,
                'sources': []
            }
        
        # Check content match score
        verified_sources = []
        total_confidence = 0.0
        contradiction_found = False
        
        for result in results:
            content = self.get_page_content(result['title'])
            if content:
                confidence = self._calculate_claim_confidence(claim, content)
                
                # Check for contradictions
                if self._check_contradiction(claim, content):
                    contradiction_found = True
                    confidence = 0.0  # Set confidence to 0 when contradiction found
                
                if confidence > 0.3:  # Threshold
                    verified_sources.append({
                        'title': result['title'],
                        'snippet': result['snippet'],
                        'confidence': confidence
                    })
                    total_confidence += confidence
        
        # If contradiction found, claim not verified
        if contradiction_found and len(verified_sources) == 0:
            return {
                'claim': claim,
                'verified': False,
                'confidence': 0.0,
                'sources': [],
                'contradiction': True
            }
        
        return {
            'claim': claim,
            'verified': len(verified_sources) > 0 and not contradiction_found,
            'confidence': min(1.0, total_confidence / len(results)) if results else 0.0,
            'sources': verified_sources
        }
    
    def verify_news_content(self, text: str) -> Dict:
        """Verify overall credibility of news content"""
        try:
            # Extract entities and claims
            entities = self._extract_entities(text)
            claims = self._extract_claims(text)
            
            # Verify entities
            entity_results = []
            for entity in entities:
                result = self.verify_entity(entity)
                entity_results.append(result)
            
            # Verify claims
            claim_results = []
            for claim in claims:
                result = self.verify_claim(claim)
                claim_results.append(result)
            
            # Calculate overall score
            entity_score = sum(r['confidence'] for r in entity_results) / len(entity_results) if entity_results else 0.0
            claim_score = sum(r['confidence'] for r in claim_results) / len(claim_results) if claim_results else 0.0
            
            # Calculate coverage
            entities_found = sum(1 for r in entity_results if r['found'])
            claims_verified = sum(1 for r in claim_results if r['verified'])
            
            total_entities = len(entity_results)
            total_claims = len(claim_results)
            
            wikipedia_coverage = (entities_found + claims_verified) / (total_entities + total_claims) if (total_entities + total_claims) > 0 else 0.0
            
            # Greatly increase entity and claim weights, and normalize
            entity_weight = 0.7  # Increased from 0.4 to 0.7
            claim_weight = 0.8   # Increased from 0.6 to 0.8
            
            # Normalize to ensure score is between 0-1
            overall_score = ((entity_score * entity_weight) + (claim_score * claim_weight)) / (entity_weight + claim_weight) if (entity_score > 0 or claim_score > 0) else 0.0
            
            return {
                'overall_score': overall_score,
                'wikipedia_coverage': wikipedia_coverage,
                'verification_summary': {
                    'entities_found': entities_found,
                    'total_entities_checked': total_entities,
                    'claims_verified': claims_verified,
                    'total_claims_checked': total_claims
                },
                'entity_results': entity_results,
                'claim_results': claim_results
            }
            
        except Exception as e:
            logger.error(f"News content verification failed: {e}")
            return {
                'overall_score': 0.0,
                'wikipedia_coverage': 0.0,
                'verification_summary': {
                    'entities_found': 0,
                    'total_entities_checked': 0,
                    'claims_verified': 0,
                    'total_claims_checked': 0
                },
                'entity_results': [],
                'claim_results': [],
                'error': str(e)
            }
    
    def _extract_entities(self, text: str) -> List[str]:
        """Extract entities from text (optimized version)"""
        # Simple entity extraction (can be improved with NER model)
        entities = []
        
        # Extract person names (capitalized words)
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
        entities.extend(names)
        
        # Extract place and organization names
        places = re.findall(r'\b[A-Z][a-z]+ (?:City|State|Country|University|Company|Corporation)\b', text)
        entities.extend(places)
        
        # Extract other capitalized proper nouns
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend([noun for noun in proper_nouns if len(noun.split()) <= 3])
        
        # Deduplicate and limit count to reduce API calls
        unique_entities = list(set(entities))[:5]  # Reduced from 10 to 5
        return unique_entities
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract claims from text (improved version)"""
        claims = []
        
        # Extract sentences containing verbs
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 200:  # Lowered minimum length requirement
                # Check if contains factual verbs
                fact_verbs = ['is', 'was', 'are', 'were', 'has', 'have', 'had', 'will', 'can', 'could', 'should', 'must', 'located', 'built', 'created', 'founded']
                if any(verb in sentence.lower() for verb in fact_verbs):
                    claims.append(sentence)
        
        # If no claims found, try broader extraction
        if not claims:
            # Split by comma, extract independent factual statements
            parts = re.split(r'[,;]', text)
            for part in parts:
                part = part.strip()
                if len(part) > 5 and len(part) < 100:
                    # Check if contains entities or numbers
                    if re.search(r'[A-Z][a-z]+|[\d]+', part):
                        claims.append(part)
        
        return claims[:5]  # Increased claim count
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # Filter stop words
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'some', 'any', 'all', 'both', 'each', 'every', 'other', 'another', 'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'}
        
        keywords = [word for word in words if word not in stop_words]
        
        # Sort by frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _calculate_claim_confidence(self, claim: str, content: str) -> float:
        """Calculate confidence of claim in content"""
        claim_words = set(claim.lower().split())
        content_words = set(content.lower().split())
        
        # Calculate word overlap
        overlap = len(claim_words.intersection(content_words))
        total_words = len(claim_words)
        
        if total_words == 0:
            return 0.0
        
        return min(1.0, overlap / total_words)
    
    def _check_contradiction(self, claim: str, content: str) -> bool:
        """Check if claim contradicts Wikipedia content"""
        claim_lower = claim.lower()
        content_lower = content.lower()
        
        # Check geographic location contradictions
        if 'located in' in claim_lower or 'is in' in claim_lower:
            # Extract location from claim
            location_match = re.search(r'located in ([^,.\n]+)|is in ([^,.\n]+)', claim_lower)
            if location_match:
                claimed_location = location_match.group(1) or location_match.group(2)
                claimed_location = claimed_location.strip()
                
                # Check if Wikipedia content has contradictory location info
                if claimed_location in content_lower:
                    # If same location found, check context
                    context_start = max(0, content_lower.find(claimed_location) - 100)
                    context_end = min(len(content_lower), content_lower.find(claimed_location) + 100)
                    context = content_lower[context_start:context_end]
                    
                    # Check for negative context
                    negative_words = ['not', 'never', 'incorrect', 'wrong', 'false', 'mistake']
                    if any(word in context for word in negative_words):
                        return True
                else:
                    # If Wikipedia doesn't mention this location, may indicate contradiction
                    return True
        
        # Check time contradictions
        if 'built in' in claim_lower or 'founded in' in claim_lower:
            year_match = re.search(r'(built|founded) in (\d{4})', claim_lower)
            if year_match:
                claimed_year = year_match.group(2)
                if claimed_year in content_lower:
                    # Check for different years
                    other_years = re.findall(r'\b(19|20)\d{2}\b', content_lower)
                    if other_years and claimed_year not in other_years:
                        return True
        
        return False
    
    def _clean_html(self, text: str) -> str:
        """Clean HTML tags"""
        return re.sub(r'<[^>]+>', '', text)