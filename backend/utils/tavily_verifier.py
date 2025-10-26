"""
Tavily Verifier - Real-time fact checking using Tavily Search API
Replaces Wikipedia verification with more comprehensive web search
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class TavilyVerifier:
    """Tavily-based fact verification"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.client = None
        self.cache = {}
        self.cache_size_limit = 1000
        
        if self.api_key:
            try:
                from tavily import TavilyClient
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("✅ Tavily client initialized successfully")
            except ImportError:
                logger.warning("⚠️ Tavily package not installed. Install with: pip install tavily-python")
                self.client = None
            except Exception as e:
                logger.error(f"❌ Failed to initialize Tavily client: {e}")
                self.client = None
        else:
            logger.warning("⚠️ TAVILY_API_KEY not found. Fact verification will be limited.")
            self.client = None
    
    def search_tavily(self, query: str, max_results: int = 5) -> List[Dict]:
        """Search using Tavily API"""
        if not self.client:
            logger.warning("Tavily client not available, returning empty results")
            return []
        
        cache_key = f"{query}_{max_results}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Tavily search with focus on factual content
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",  # More thorough search
                include_answer=True,  # Get AI-generated answer
                include_domains=["wikipedia.org", "reuters.com", "bbc.com", "apnews.com"],  # Prioritize reliable sources
            )
            
            results = []
            
            # Extract answer if available
            answer = response.get('answer', '')
            
            # Extract search results
            for item in response.get('results', []):
                results.append({
                    'title': item.get('title', ''),
                    'content': item.get('content', ''),
                    'url': item.get('url', ''),
                    'score': item.get('score', 0),
                    'published_date': item.get('published_date', '')
                })
            
            result = {
                'answer': answer,
                'results': results,
                'query': query
            }
            
            # Manage cache size
            if len(self.cache) >= self.cache_size_limit:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Tavily search failed for query '{query}': {e}")
            return {'answer': '', 'results': [], 'query': query}
    
    def verify_entity(self, entity: str) -> Dict:
        """Verify if an entity exists and is credible"""
        search_result = self.search_tavily(entity, max_results=3)
        
        if not search_result or not search_result.get('results'):
            return {
                'entity': entity,
                'exists': False,
                'confidence': 0.0,
                'summary': None,
                'sources': []
            }
        
        results = search_result.get('results', [])
        
        # Calculate confidence based on number of reliable sources
        confidence = min(len(results) / 3.0, 1.0)
        
        # Get top result summary
        summary = results[0].get('content', '')[:500] if results else None
        
        # Extract source URLs
        sources = [r.get('url', '') for r in results[:3]]
        
        return {
            'entity': entity,
            'exists': True,
            'confidence': confidence,
            'summary': summary,
            'sources': sources,
            'answer': search_result.get('answer', '')
        }
    
    def verify_claim(self, claim: str) -> Dict:
        """Verify a specific claim"""
        # Search for the claim
        search_result = self.search_tavily(f"fact check: {claim}", max_results=5)
        
        if not search_result:
            return {
                'claim': claim,
                'verified': False,
                'confidence': 0.0,
                'evidence': [],
                'verdict': 'unknown'
            }
        
        results = search_result.get('results', [])
        answer = search_result.get('answer', '')
        
        # Analyze answer and results for verification
        evidence = []
        for result in results:
            evidence.append({
                'source': result.get('url', ''),
                'title': result.get('title', ''),
                'snippet': result.get('content', '')[:200],
                'score': result.get('score', 0)
            })
        
        # Simple verdict based on answer and number of sources
        verdict = 'unknown'
        confidence = 0.5
        
        if answer:
            answer_lower = answer.lower()
            if any(word in answer_lower for word in ['true', 'confirmed', 'verified', 'accurate']):
                verdict = 'true'
                confidence = min(len(results) / 5.0, 0.9)
            elif any(word in answer_lower for word in ['false', 'fake', 'misleading', 'unverified']):
                verdict = 'false'
                confidence = min(len(results) / 5.0, 0.9)
        
        return {
            'claim': claim,
            'verified': len(results) > 0,
            'confidence': confidence,
            'evidence': evidence,
            'verdict': verdict,
            'answer': answer,
            'sources_count': len(results)
        }
    
    def comprehensive_verification(self, text: str, entities: List[str], claims: List[str]) -> Dict:
        """
        Comprehensive fact verification
        Compatible with Wikipedia verifier interface
        """
        if not self.client:
            return {
                'verification_score': 0.5,
                'entity_coverage': 0.0,
                'claim_accuracy': 0.0,
                'entities_checked': 0,
                'entities_found': 0,
                'claims_checked': 0,
                'claims_verified': 0,
                'details': 'Tavily client not available'
            }
        
        # Verify entities
        entity_results = []
        entities_found = 0
        for entity in entities[:5]:  # Limit to 5 entities to save API calls
            result = self.verify_entity(entity)
            entity_results.append(result)
            if result['exists'] and result['confidence'] > 0.5:
                entities_found += 1
        
        # Verify claims
        claim_results = []
        claims_verified = 0
        for claim in claims[:3]:  # Limit to 3 claims
            result = self.verify_claim(claim)
            claim_results.append(result)
            if result['verified'] and result['verdict'] == 'true':
                claims_verified += 1
        
        # Calculate metrics
        entities_checked = len(entity_results)
        claims_checked = len(claim_results)
        
        entity_coverage = entities_found / entities_checked if entities_checked > 0 else 0.0
        claim_accuracy = claims_verified / claims_checked if claims_checked > 0 else 0.5
        
        # Overall verification score (weighted average)
        verification_score = (entity_coverage * 0.4 + claim_accuracy * 0.6)
        
        return {
            'verification_score': verification_score,
            'entity_coverage': entity_coverage,
            'claim_accuracy': claim_accuracy,
            'entities_checked': entities_checked,
            'entities_found': entities_found,
            'claims_checked': claims_checked,
            'claims_verified': claims_verified,
            'entity_results': entity_results,
            'claim_results': claim_results,
            'provider': 'tavily'
        }
    
    def quick_check(self, text: str) -> float:
        """
        Enhanced quick fact check with targeted verification
        Compatible with Wikipedia verifier interface
        """
        logger.info("🔍 DEBUG: quick_check method called!")
        logger.info(f"🔍 DEBUG: self.client = {self.client}")
        
        if not self.client:
            logger.warning("⚠️ Tavily client not available, returning default score 0.5")
            return 0.5
        
        try:
            import re
            
            logger.info(f"🔍 Tavily quick check starting, text length: {len(text)}, text preview: {text[:100]}")
            
            # Extract key information
            dates = re.findall(r'\b(18|19|20)\d{2}\b', text)
            logger.info(f"🔍 Tavily: Extracted dates: {dates}")
            
            # Step 1: General topic search - Increased from 3 to 5 for better coverage
            search_result = self.search_tavily(text[:200], max_results=5)
            logger.info(f"🔍 Tavily search completed, results: {len(search_result.get('results', []))}")
            
            if not search_result or not search_result.get('results'):
                logger.info(f"🔍 Tavily: No search results found, returning 0.3")
                return 0.3  # Low confidence if no results
            
            results = search_result.get('results', [])
            answer = search_result.get('answer', '').lower()
            
            # NEW APPROACH: Extract and match entities/information
            # Extract key entities from the text
            extracted_info = set()
            # Extract names (capitalized words, 2+ chars)
            names = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text[:200])
            extracted_info.update(names[:15])  # Limit to first 15 names
            # Extract locations (common patterns)
            locations = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:City|Country|State|Nation)\b', text[:200])
            extracted_info.update(locations[:5])
            # Extract organizations (common patterns)
            organizations = re.findall(r'\b(?:The|A)\s+[A-Z][A-Za-z]+\s+(?:Company|Institute|University|Society|Organization)\b', text[:200])
            extracted_info.update(organizations[:5])
            
            logger.info(f"📝 Extracted entities: {list(extracted_info)[:5]}")
            
            # Count how many of these appear in search results
            matched_count = 0
            all_result_text = ' '.join([r.get('content', '').lower() for r in results]) + ' ' + answer
            
            for info in extracted_info:
                if info.lower() in all_result_text:
                    matched_count += 1
            
            # Calculate ratio: matched entities / total extracted entities
            total_extracted = len(extracted_info)
            
            # If no entities extracted, fall back to result-count-based scoring
            if total_extracted == 0:
                base_score = len(results) / 5.0  # Simple result-based score
                logger.info(f"🔍 Tavily: No entities extracted, using result-based scoring: {base_score:.3f}")
            else:
                # Simple ratio: matched / total extracted
                base_score = matched_count / total_extracted
                logger.info(f"🔍 Tavily: Extracted {total_extracted} entities, matched {matched_count}")
                logger.info(f"🔍 Tavily: Score = {matched_count}/{total_extracted} = {base_score:.3f}")
            logger.info(f"📝 Tavily: Answer content: {answer[:200]}")
            
            # Step 2: If there are specific dates, do targeted fact checking
            if dates:
                logger.info(f"🔍 Tavily: Detected dates {dates}, performing targeted fact check")
                
                # Perform fact check query
                fact_check_query = f"when was {text[:100]} fact check"
                fact_result = self.search_tavily(fact_check_query, max_results=5)
                
                if fact_result and fact_result.get('results'):
                    fact_answer = fact_result.get('answer', '').lower()
                    fact_results = fact_result.get('results', [])
                    
                    # Combine all content for analysis
                    all_content = fact_answer + ' ' + ' '.join([r.get('content', '') for r in fact_results[:2]])
                    all_content_lower = all_content.lower()
                    
                    logger.info(f"🔍 Tavily: Fact check answer length: {len(fact_answer)} chars")
                    
                    # Check if the stated date appears in reliable sources
                    dates_in_text = [d for d in dates]
                    dates_in_sources = re.findall(r'\b(18|19|20)\d{2}\b', all_content)
                    
                    # If the date from the claim doesn't appear in fact check results, it's suspicious
                    date_mismatch = False
                    for claim_date in dates_in_text:
                        if claim_date not in dates_in_sources:
                            logger.info(f"⚠️ Tavily: Date {claim_date} from claim NOT found in sources")
                            date_mismatch = True
                    
                    # Check for explicit contradictions
                    contradiction_words = ['false', 'incorrect', 'wrong', 'actually', 'not true', 'debunked', 'misleading', 'myth']
                    has_contradiction = any(word in all_content_lower for word in contradiction_words)
                    
                    # Check for confirmations
                    confirmation_words = ['correct', 'accurate', 'confirmed', 'verified', 'true', 'indeed']
                    has_confirmation = any(word in all_content_lower for word in confirmation_words)
                    
                    logger.info(f"🔍 Tavily: Date mismatch={date_mismatch}, contradiction={has_contradiction}, confirmation={has_confirmation}")
                    
                    # Adjust score based on findings
                    if date_mismatch or has_contradiction:
                        # If date doesn't match or explicit contradiction found
                        base_score *= 0.3  # Severe penalty
                        logger.info(f"⚠️ Tavily: CONTRADICTION detected, reducing score to {base_score:.3f}")
                    elif has_confirmation:
                        # If explicitly confirmed
                        base_score = min(base_score + 0.3, 0.8)
                        logger.info(f"✅ Tavily: CONFIRMATION found, increasing score to {base_score:.3f}")
            
            # Additional checks on the main answer
            if answer:
                if any(word in answer for word in ['false', 'incorrect', 'wrong', 'not true']):
                    base_score *= 0.3
                    logger.info(f"⚠️ Tavily: Main answer suggests false claim")
                elif any(word in answer for word in ['true', 'correct', 'accurate']):
                    base_score = min(base_score + 0.1, 0.8)
                    logger.info(f"✅ Tavily: Main answer suggests true claim")
            
            final_score = min(max(base_score, 0.1), 1.0)
            logger.info(f"🎯 Tavily final verification score: {final_score:.3f}")
            
            return final_score
            
        except Exception as e:
            import traceback
            logger.error(f"❌ Tavily quick check failed: {e}")
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return 0.5

