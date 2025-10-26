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
        # 增加缓存大小和超时设置
        self.cache = {}
        self.cache_size_limit = 1000  # 限制缓存大小
        self.timeout = 5  # 减少超时时间
        
    def search_wikipedia(self, query: str, limit: int = 5) -> List[Dict]:
        """搜索Wikipedia页面"""
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
            
            # 管理缓存大小
            if len(self.cache) >= self.cache_size_limit:
                # 删除最旧的缓存项
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
            
            self.cache[cache_key] = results
            return results
        except Exception as e:
            logger.error(f"Wikipedia search failed for query '{query}': {e}")
            return []
    
    def get_page_content(self, title: str) -> Optional[str]:
        """获取Wikipedia页面内容"""
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
        """验证实体是否在Wikipedia中存在"""
        results = self.search_wikipedia(entity, limit=3)
        
        if not results:
            return {
                'entity': entity,
                'found': False,
                'confidence': 0.0,
                'sources': []
            }
        
        # 检查标题匹配度
        best_match = None
        best_score = 0.0
        
        for result in results:
            title = result['title'].lower()
            entity_lower = entity.lower()
            
            # 计算匹配分数
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
        """验证声明是否在Wikipedia中得到支持"""
        # 提取关键词进行搜索
        keywords = self._extract_keywords(claim)
        if not keywords:
            return {
                'claim': claim,
                'verified': False,
                'confidence': 0.0,
                'sources': []
            }
        
        # 搜索相关页面
        search_query = ' '.join(keywords[:3])  # 使用前3个关键词
        results = self.search_wikipedia(search_query, limit=5)
        
        if not results:
            return {
                'claim': claim,
                'verified': False,
                'confidence': 0.0,
                'sources': []
            }
        
        # 检查内容匹配度
        verified_sources = []
        total_confidence = 0.0
        contradiction_found = False
        
        for result in results:
            content = self.get_page_content(result['title'])
            if content:
                confidence = self._calculate_claim_confidence(claim, content)
                
                # 检查是否存在矛盾
                if self._check_contradiction(claim, content):
                    contradiction_found = True
                    confidence = 0.0  # 发现矛盾时置信度为0
                
                if confidence > 0.3:  # 阈值
                    verified_sources.append({
                        'title': result['title'],
                        'snippet': result['snippet'],
                        'confidence': confidence
                    })
                    total_confidence += confidence
        
        # 如果发现矛盾，声明未验证
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
        """验证新闻内容的整体可信度"""
        try:
            # 提取实体和声明
            entities = self._extract_entities(text)
            claims = self._extract_claims(text)
            
            # 验证实体
            entity_results = []
            for entity in entities:
                result = self.verify_entity(entity)
                entity_results.append(result)
            
            # 验证声明
            claim_results = []
            for claim in claims:
                result = self.verify_claim(claim)
                claim_results.append(result)
            
            # 计算综合得分
            entity_score = sum(r['confidence'] for r in entity_results) / len(entity_results) if entity_results else 0.0
            claim_score = sum(r['confidence'] for r in claim_results) / len(claim_results) if claim_results else 0.0
            
            # 计算覆盖率
            entities_found = sum(1 for r in entity_results if r['found'])
            claims_verified = sum(1 for r in claim_results if r['verified'])
            
            total_entities = len(entity_results)
            total_claims = len(claim_results)
            
            wikipedia_coverage = (entities_found + claims_verified) / (total_entities + total_claims) if (total_entities + total_claims) > 0 else 0.0
            
            # 🔥 大大提高实体和声明的权重，并进行归一化
            entity_weight = 0.7  # 从 0.4 大大提高 to 0.7
            claim_weight = 0.8   # 从 0.6 大大提高 to 0.8
            
            # 归一化处理，确保得分在0-1之间
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
        """提取文本中的实体（优化版本）"""
        # 简单的实体提取（可以改进为使用NER模型）
        entities = []
        
        # 提取人名（大写字母开头的单词）
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', text)
        entities.extend(names)
        
        # 提取地名和组织名
        places = re.findall(r'\b[A-Z][a-z]+ (?:City|State|Country|University|Company|Corporation)\b', text)
        entities.extend(places)
        
        # 提取其他大写开头的专有名词
        proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        entities.extend([noun for noun in proper_nouns if len(noun.split()) <= 3])
        
        # 去重并限制数量，减少API调用
        unique_entities = list(set(entities))[:5]  # 从10减少到5
        return unique_entities
    
    def _extract_claims(self, text: str) -> List[str]:
        """提取文本中的声明（改进版本）"""
        claims = []
        
        # 提取包含动词的句子
        sentences = re.split(r'[.!?]+', text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and len(sentence) < 200:  # 降低最小长度要求
                # 检查是否包含事实性动词
                fact_verbs = ['is', 'was', 'are', 'were', 'has', 'have', 'had', 'will', 'can', 'could', 'should', 'must', 'located', 'built', 'created', 'founded']
                if any(verb in sentence.lower() for verb in fact_verbs):
                    claims.append(sentence)
        
        # 如果没有找到声明，尝试更宽泛的提取
        if not claims:
            # 按逗号分割，提取独立的事实陈述
            parts = re.split(r'[,;]', text)
            for part in parts:
                part = part.strip()
                if len(part) > 5 and len(part) < 100:
                    # 检查是否包含实体或数字
                    if re.search(r'[A-Z][a-z]+|[\d]+', part):
                        claims.append(part)
        
        return claims[:5]  # 增加声明数量
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        
        # 过滤停用词
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'a', 'an', 'some', 'any', 'all', 'both', 'each', 'every', 'other', 'another', 'such', 'no', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now'}
        
        keywords = [word for word in words if word not in stop_words]
        
        # 按频率排序
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:10]]
    
    def _calculate_claim_confidence(self, claim: str, content: str) -> float:
        """计算声明在内容中的置信度"""
        claim_words = set(claim.lower().split())
        content_words = set(content.lower().split())
        
        # 计算词汇重叠度
        overlap = len(claim_words.intersection(content_words))
        total_words = len(claim_words)
        
        if total_words == 0:
            return 0.0
        
        return min(1.0, overlap / total_words)
    
    def _check_contradiction(self, claim: str, content: str) -> bool:
        """检查声明是否与Wikipedia内容矛盾"""
        claim_lower = claim.lower()
        content_lower = content.lower()
        
        # 检查地理位置矛盾
        if 'located in' in claim_lower or 'is in' in claim_lower:
            # 提取声明中的地点
            location_match = re.search(r'located in ([^,.\n]+)|is in ([^,.\n]+)', claim_lower)
            if location_match:
                claimed_location = location_match.group(1) or location_match.group(2)
                claimed_location = claimed_location.strip()
                
                # 检查Wikipedia内容中是否有矛盾的地点信息
                if claimed_location in content_lower:
                    # 如果找到相同地点，检查上下文
                    context_start = max(0, content_lower.find(claimed_location) - 100)
                    context_end = min(len(content_lower), content_lower.find(claimed_location) + 100)
                    context = content_lower[context_start:context_end]
                    
                    # 检查是否有否定的上下文
                    negative_words = ['not', 'never', 'incorrect', 'wrong', 'false', 'mistake']
                    if any(word in context for word in negative_words):
                        return True
                else:
                    # 如果Wikipedia中没有提到该地点，可能表示矛盾
                    return True
        
        # 检查时间矛盾
        if 'built in' in claim_lower or 'founded in' in claim_lower:
            year_match = re.search(r'(built|founded) in (\d{4})', claim_lower)
            if year_match:
                claimed_year = year_match.group(2)
                if claimed_year in content_lower:
                    # 检查是否有不同的年份
                    other_years = re.findall(r'\b(19|20)\d{2}\b', content_lower)
                    if other_years and claimed_year not in other_years:
                        return True
        
        return False
    
    def _clean_html(self, text: str) -> str:
        """清理HTML标签"""
        return re.sub(r'<[^>]+>', '', text)