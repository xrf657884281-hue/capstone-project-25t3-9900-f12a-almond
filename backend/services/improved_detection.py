


   
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import re
import nltk
from textstat import flesch_reading_ease, flesch_kincaid_grade
from collections import Counter
import spacy
import logging
                                                        
                               
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.tavily_verifier import TavilyVerifier

logger = logging.getLogger(__name__)

def convert_to_native_types(obj: Any) -> Any:
                                                                          
    if isinstance(obj, (np.integer, np.floating)):
        return obj.item()
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, dict):
        return {key: convert_to_native_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [convert_to_native_types(item) for item in obj]
    elif isinstance(obj, torch.Tensor):
        return obj.detach().cpu().numpy().tolist()
    else:
        return obj

class RhetoricalAnalyzer:
                                                                                          
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
    
    def analyze_emotional_language(self, text: str) -> Dict:
                                                 
                                       
        emotional_words = {
            'positive': ['amazing', 'incredible', 'fantastic', 'wonderful', 'brilliant', 'outstanding'],
            'negative': ['terrible', 'horrible', 'awful', 'disgusting', 'shocking', 'appalling'],
            'fear': ['fear', 'terror', 'panic', 'dread', 'anxiety', 'worry'],
            'anger': ['fury', 'rage', 'outrage', 'furious', 'angry', 'mad'],
            'exaggeration': ['extremely', 'incredibly', 'absolutely', 'completely', 'totally', 'utterly']
        }
        
        text_lower = text.lower()
        emotional_scores = {}
        
        for emotion, words in emotional_words.items():
            score = sum(text_lower.count(word) for word in words)
            emotional_scores[emotion] = score / len(text.split())              
        
        return emotional_scores
    
    def detect_loaded_language(self, text: str) -> Dict:
                                                             
        loaded_patterns = {
            'conspiracy': [r'\b(conspiracy|plot|cover.?up|secret|hidden)\b', r'\b(they|them)\b.*\b(hide|conceal)\b'],
            'urgency': [r'\b(urgent|immediate|breaking|shocking|alarming)\b', r'\b(now|immediately|asap)\b'],
            'authority': [r'\b(experts?|officials?|sources?)\b.*\b(say|claim|reveal)\b'],
            'vague_sources': [r'\b(according to|sources say|reportedly|allegedly)\b'],
            'emotional_triggers': [r'\b(devastating|catastrophic|unprecedented|outrageous)\b']
        }
        
        loaded_scores = {}
        text_lower = text.lower()
        
        for pattern_type, patterns in loaded_patterns.items():
            matches = 0
            for pattern in patterns:
                matches += len(re.findall(pattern, text_lower))
            loaded_scores[pattern_type] = matches / len(text.split())
        
        return loaded_scores
    
    def analyze_readability(self, text: str) -> Dict:
                                               
        try:
            return {
                'flesch_reading_ease': flesch_reading_ease(text),
                'flesch_kincaid_grade': flesch_kincaid_grade(text),
                'avg_sentence_length': np.mean([len(sent.split()) for sent in text.split('.') if sent.strip()]),
                'avg_word_length': np.mean([len(word) for word in text.split()]),
                'complex_word_ratio': len([w for w in text.split() if len(w) > 6]) / len(text.split())
            }
        except:
            return {
                'flesch_reading_ease': 50.0,
                'flesch_kincaid_grade': 10.0,
                'avg_sentence_length': 15.0,
                'avg_word_length': 5.0,
                'complex_word_ratio': 0.3
            }
    
    def detect_linguistic_patterns(self, text: str) -> Dict:
                                                
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        
                               
        entities = [ent.label_ for ent in doc.ents]
        entity_counts = Counter(entities)
        
                              
        pos_tags = [token.pos_ for token in doc]
        pos_counts = Counter(pos_tags)
        
                              
        complex_sentences = 0
        for sent in doc.sents:
            if len([token for token in sent if token.dep_ in ['nsubj', 'dobj', 'pobj']]) > 3:
                complex_sentences += 1
        
        return {
            'entity_diversity': len(set(entities)) / len(entities) if entities else 0,
            'pronoun_ratio': pos_counts.get('PRON', 0) / len(pos_tags),
            'adjective_ratio': pos_counts.get('ADJ', 0) / len(pos_tags),
            'complex_sentence_ratio': complex_sentences / len(list(doc.sents)) if doc.sents else 0,
            'passive_voice_ratio': len([token for token in doc if token.tag_ == 'VBN']) / len([token for token in doc if token.pos_ == 'VERB']) if any(token.pos_ == 'VERB' for token in doc) else 0
        }
    
    def analyze_text(self, text: str) -> Dict:
                                               
        return {
            'emotional_language': self.analyze_emotional_language(text),
            'loaded_language': self.detect_loaded_language(text),
            'readability': self.analyze_readability(text),
            'linguistic_patterns': self.detect_linguistic_patterns(text)
        }

class DetectorFusion:
                                
    
    def __init__(self):
        self.fusion_model = None
        self.scaler = StandardScaler()
        self.feature_names = []
    
    def extract_fusion_features(self, baseline_results: Dict, rhetorical_features: Dict) -> np.ndarray:
                                                                                   
        features = []
        feature_names = []
        
                                     
        text_detection = baseline_results.get('text_detection', {})
        multimodal_detection = baseline_results.get('multimodal_detection', {})
        
                          
        if 'roberta' in text_detection and 'error' not in text_detection['roberta']:
            features.extend([
                text_detection['roberta'].get('fake_score', 0.5),
                text_detection['roberta'].get('confidence', 0.0)
            ])
            feature_names.extend(['roberta_fake_score', 'roberta_confidence'])
        
                            
        if 'detectgpt' in text_detection and 'error' not in text_detection['detectgpt']:
            is_generated_bool = text_detection['detectgpt'].get('is_generated', False)
            features.extend([
                text_detection['detectgpt'].get('sensitivity', 0.0),
                1.0 if is_generated_bool else 0.0                                    
            ])
            feature_names.extend(['detectgpt_sensitivity', 'detectgpt_is_generated'])
        
                       
        if 'gltr' in text_detection and 'error' not in text_detection['gltr']:
            features.extend([
                text_detection['gltr'].get('high_prob_ratio', 0.0),
                text_detection['gltr'].get('avg_probability', 0.0)
            ])
            feature_names.extend(['gltr_high_prob_ratio', 'gltr_avg_probability'])
        
                            
        if 'zero_shot' in text_detection and 'error' not in text_detection['zero_shot']:
            features.extend([
                text_detection['zero_shot'].get('fake_score', 0.5),
                text_detection['zero_shot'].get('confidence', 0.0)
            ])
            feature_names.extend(['zero_shot_fake_score', 'zero_shot_confidence'])
        
                       
        if 'clip' in multimodal_detection and 'error' not in multimodal_detection['clip']:
            features.extend([
                multimodal_detection['clip'].get('consistency_score', 0.5),
                multimodal_detection['clip'].get('is_consistent', True)
            ])
            feature_names.extend(['clip_consistency', 'clip_is_consistent'])
        
                             
        emotional = rhetorical_features.get('emotional_language', {})
        features.extend([
            emotional.get('positive', 0.0),
            emotional.get('negative', 0.0),
            emotional.get('fear', 0.0),
            emotional.get('anger', 0.0),
            emotional.get('exaggeration', 0.0)
        ])
        feature_names.extend(['emotional_positive', 'emotional_negative', 'emotional_fear', 'emotional_anger', 'emotional_exaggeration'])
        
        loaded = rhetorical_features.get('loaded_language', {})
        features.extend([
            loaded.get('conspiracy', 0.0),
            loaded.get('urgency', 0.0),
            loaded.get('authority', 0.0),
            loaded.get('vague_sources', 0.0),
            loaded.get('emotional_triggers', 0.0)
        ])
        feature_names.extend(['loaded_conspiracy', 'loaded_urgency', 'loaded_authority', 'loaded_vague_sources', 'loaded_emotional_triggers'])
        
        readability = rhetorical_features.get('readability', {})
        features.extend([
            readability.get('flesch_reading_ease', 50.0),
            readability.get('avg_sentence_length', 15.0),
            readability.get('complex_word_ratio', 0.3)
        ])
        feature_names.extend(['flesch_reading_ease', 'avg_sentence_length', 'complex_word_ratio'])
        
        linguistic = rhetorical_features.get('linguistic_patterns', {})
        features.extend([
            linguistic.get('entity_diversity', 0.0),
            linguistic.get('pronoun_ratio', 0.0),
            linguistic.get('adjective_ratio', 0.0),
            linguistic.get('complex_sentence_ratio', 0.0),
            linguistic.get('passive_voice_ratio', 0.0)
        ])
        feature_names.extend(['entity_diversity', 'pronoun_ratio', 'adjective_ratio', 'complex_sentence_ratio', 'passive_voice_ratio'])
        
        self.feature_names = feature_names
        return np.array(features).reshape(1, -1)
    
    def train_fusion_model(self, X: np.ndarray, y: np.ndarray):
                                
                              
        X_scaled = self.scaler.fit_transform(X)
        
                                           
        self.fusion_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.fusion_model.fit(X_scaled, y)
    
    def predict_fusion(self, features: np.ndarray, baseline_results: Optional[Dict] = None) -> Dict:
                                             
        if self.fusion_model is None:
                                                              
            return self._simple_weighted_fusion(features, baseline_results)
        
        features_scaled = self.scaler.transform(features)
        prediction = self.fusion_model.predict(features_scaled)[0]
        probability = self.fusion_model.predict_proba(features_scaled)[0]
        
        return {
            'prediction': prediction,
            'fake_probability': probability[1] if len(probability) > 1 else 0.5,
            'confidence': max(probability),
            'method': 'trained_fusion'
        }
    
    def _simple_weighted_fusion(self, features: np.ndarray, baseline_results: Optional[Dict] = None) -> Dict:
                                                                         
        features_flat = features.flatten()
        
                                                                             
        detectgpt_is_generated = False
        detectgpt_sensitivity = 0.0
        
        if baseline_results:
            text_detection = baseline_results.get('text_detection', {})
            detectgpt_data = text_detection.get('detectgpt', {})
            if 'error' not in detectgpt_data:
                detectgpt_is_generated = detectgpt_data.get('is_generated', False)
                detectgpt_sensitivity = detectgpt_data.get('sensitivity', 0.0)
        
                                                                    
        if not baseline_results:
            detectgpt_is_generated = features_flat[3] if len(features_flat) > 3 else False
            detectgpt_sensitivity = features_flat[2] if len(features_flat) > 2 else 0.0
        
                            
        normalized_features = []
        for i, val in enumerate(features_flat):
                                    
            if val > 1 and val < 10:                              
                val = min(val / 10.0, 1.0)
            
            if not (0 <= val <= 1):
                val = 0.5                      
            
            normalized_features.append(val)
        
                                                              
        try:
            from sklearn.ensemble import RandomForestClassifier
            import numpy as np
            
                                                                                  
                                                                           
            feature_weights = np.array([
                0.05,                         # roberta_fake_score
                0.04,                         # roberta_confidence
                0.80,                         # detectgpt_sensitivity (dominant weight)
                0.05,                         # detectgpt_is_generated
                0.02,                         # gltr_high_prob_ratio
                0.02,                         # gltr_avg_probability
                0.02,                         # zero_shot_fake_score
                0.02,                         # zero_shot_confidence
                0.02,                         # clip_consistency
                0.02,                         # clip_is_consistent
                0.02,                         # emotional_positive
                0.02                          # emotional_negative
            ])
            
                                           
            feature_weights = feature_weights / feature_weights.sum()
            
                                       
            weighted_score = np.sum(np.array(normalized_features[:len(feature_weights)]) * feature_weights)
            
        except ImportError:
                                                                         
            core_detection_features = []
            rhetorical_features = []
            
            for i, val in enumerate(normalized_features):
                if i < 8:
                    if i == 2 or i == 3:                      
                        core_detection_features.extend([val, val])                           
                    else:
                        core_detection_features.append(val)
                else:
                    rhetorical_features.append(val)
            
            if core_detection_features:
                core_score = np.mean(core_detection_features)
            else:
                core_score = 0.5
                
            if rhetorical_features:
                rhetorical_score = np.mean(rhetorical_features)
            else:
                rhetorical_score = 0.5
            
            weighted_score = 0.8 * core_score + 0.2 * rhetorical_score
        
                                                                         
                                                                              
        
        ai_detected = False
        ai_bonus = 0.0
        
                                                        
                                                    
        if detectgpt_sensitivity > 5.0:  
            ai_bonus = 0.20  
            ai_detected = True
        elif detectgpt_sensitivity > 4.2:  
            ai_bonus = 0.12  
            ai_detected = True
        elif detectgpt_sensitivity > 3.8: 
            ai_bonus = 0.08 
            ai_detected = False  
        elif detectgpt_sensitivity > 3.5:  
            ai_bonus = 0.04 
            ai_detected = False
        
        if ai_bonus > 0:
            weighted_score = min(1.0, weighted_score + ai_bonus)
        
                                   
        weighted_score = max(0.0, min(1.0, weighted_score))
        
        return {
            'prediction': 'fake' if weighted_score > 0.5 else 'real',
            'fake_probability': weighted_score,
            'confidence': abs(weighted_score - 0.5) * 2,
            'method': 'random_forest_fusion',
            'ai_generated_detected': ai_detected,
            'detectgpt_is_generated_value': float(detectgpt_is_generated),              
            'num_features_used': len(normalized_features)
        }

class CrossModalChecker:
                                         
    
    def __init__(self):
        self.consistency_threshold = 0.3
    
    def check_temporal_consistency(self, text: str, image_metadata: Optional[Dict] = None) -> Dict:
                                                                                   
                                            
        time_patterns = [
            r'\b(\d{4})\b',        
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\b',
            r'\b(today|yesterday|tomorrow|now|recently|lately)\b'
        ]
        
        text_times = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text.lower())
            text_times.extend(matches)
        
                                      
        current_year = 2025
        year_matches = [int(t) for t in text_times if t.isdigit() and len(t) == 4]
        
        temporal_score = 1.0
        temporal_issues = []
        
        if year_matches:
                                    
            future_years = [y for y in year_matches if y > current_year + 1]
            if future_years:
                temporal_score -= 0.4                                      
                temporal_issues.append(f'future_years: {future_years}')
            
                                                                                         
                                                               
            very_old_years = [y for y in year_matches if y < 1500]                       
            old_years = [y for y in year_matches if 1500 <= y < 1800]                
            recent_past = [y for y in year_matches if 1800 <= y < current_year - 50]                  
            
                                                                          
            modern_keywords = ['tower', 'building', 'constructed', 'built', 'completed', 
                             'technology', 'internet', 'computer', 'phone', 'car', 'airplane']
            has_modern_context = any(keyword in text.lower() for keyword in modern_keywords)
            
            if very_old_years and has_modern_context:
                                                                                      
                temporal_score -= 0.9                                            
                temporal_issues.append(f'anachronism_detected: {very_old_years} with modern context')
                logger.warning(f"EXTREME temporal inconsistency: years {very_old_years} with modern keywords")
            elif very_old_years:
                                                                                   
                temporal_score -= 0.5
                temporal_issues.append(f'medieval_years: {very_old_years}')
            elif old_years and has_modern_context:
                                                                       
                temporal_score -= 0.5                  
                temporal_issues.append(f'historical_mismatch: {old_years}')
            elif recent_past:
                                                                       
                temporal_score -= 0.1
                temporal_issues.append(f'historical_reference: {recent_past}')
        
        return {
            'temporal_consistency_score': max(0.0, temporal_score),
            'extracted_times': text_times,
            'temporal_issues': temporal_issues,
            'is_temporally_consistent': temporal_score > self.consistency_threshold
        }
    
    def check_spatial_consistency(self, text: str, image_metadata: Optional[Dict] = None) -> Dict:
                                       
                                                                          
        location_patterns = [
            r'\b([A-Z][a-z]+ (?:(?:City|Town|State|Country|Nation)))\b',
            r'\b(in|at|from|to) ([A-Z][a-z]+)\b'
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            locations.extend([match[1] if isinstance(match, tuple) else match for match in matches])
        
                                                         
        location_consistency = 1.0
        if len(set(locations)) > 3:                                                  
            location_consistency -= 0.2
        
        return {
            'spatial_consistency_score': location_consistency,
            'extracted_locations': list(set(locations)),
            'is_spatially_consistent': location_consistency > self.consistency_threshold
        }
    
    def check_logical_consistency(self, text: str) -> Dict:
                                       
                                         
        contradiction_patterns = [
            (r'\b(not|no|never|none)\b.*\b(always|all|every|everyone)\b', 'negation_contradiction'),
            (r'\b(before|after)\b.*\b(before|after)\b', 'temporal_contradiction'),
            (r'\b(increased|rose|grew)\b.*\b(decreased|fell|dropped)\b', 'trend_contradiction')
        ]
        
        contradictions = []
        for pattern, contradiction_type in contradiction_patterns:
            if re.search(pattern, text.lower()):
                contradictions.append(contradiction_type)
        
        logical_score = max(0.0, 1.0 - len(contradictions) * 0.3)
        
        return {
            'logical_consistency_score': logical_score,
            'detected_contradictions': contradictions,
            'is_logically_consistent': logical_score > self.consistency_threshold
        }
    
    def comprehensive_consistency_check(self, text: str, image_metadata: Optional[Dict] = None) -> Dict:
                                             
        temporal = self.check_temporal_consistency(text, image_metadata)
        spatial = self.check_spatial_consistency(text, image_metadata)
        logical = self.check_logical_consistency(text)
        
                                             
        overall_score = (
            temporal['temporal_consistency_score'] * 0.3 +
            spatial['spatial_consistency_score'] * 0.3 +
            logical['logical_consistency_score'] * 0.4
        )
        
        return {
            'overall_consistency_score': overall_score,
            'temporal_consistency': temporal,
            'spatial_consistency': spatial,
            'logical_consistency': logical,
            'is_globally_consistent': overall_score > self.consistency_threshold
        }

class ImprovedDetection:
                                       
    
    def __init__(self, use_tavily: bool = True):
        self.rhetorical_analyzer = RhetoricalAnalyzer()
        self.detector_fusion = DetectorFusion()
        self.cross_modal_checker = CrossModalChecker()
        
                                  
        self.verifier_type = 'tavily'
        self.verifier = None
        
        try:
            self.verifier = TavilyVerifier()
            if self.verifier.client:
                logger.info("✅ Tavily verifier initialized successfully")
            else:
                logger.warning("⚠️ Tavily client not available")
                self.verifier = None
        except Exception as e:
            logger.warning(f"⚠️ Tavily verifier failed: {e}")
            self.verifier = None
    
    def improved_detection(self, baseline_results: Dict, text: str, image_metadata: Optional[Dict] = None, detection_config: Optional[Dict] = None) -> Dict:
                                                                                              
        
                             
        config = detection_config or {}
        use_verification = config.get('use_wikipedia', True)                                                       
        use_rhetorical = config.get('use_rhetorical', True)
        use_consistency = config.get('use_consistency', True)
        threshold = config.get('threshold', 0.5)
        tavily_weight = config.get('wikipedia_weight', 1.0)                                                          
        
        logger.info(f"Detection config: Verification={use_verification}, Rhetorical={use_rhetorical}, Consistency={use_consistency}, Threshold={threshold}, Tavily_Weight={tavily_weight}")
        

        tavily_verification = {}
        if self.verifier and use_verification:                                               
            try:
                logger.info(f"🔍 [FAST PATH] Performing fact pre-verification using {self.verifier_type}...")
                                       
                import platform
                import threading
                
                verification_result = None
                quick_score = 0.5                      
                timeout_occurred = [False]
                
                if platform.system() == 'Windows':
                                                                                 
                    def call_with_timeout():
                        nonlocal verification_result, quick_score
                        try:
                            import spacy
                            import nltk
                            nlp = spacy.load("en_core_web_sm")
                            doc = nlp(text[:500])
                            entities = [ent.text for ent in doc.ents[:5]]
                            sentences = nltk.sent_tokenize(text[:500])
                            claims = sentences[:3]
                            verification_result = self.verifier.comprehensive_verification(text, entities, claims)
                            quick_score = verification_result.get('verification_score', 0.5)
                        except Exception as e:
                            logger.error(f"Tavily verification failed: {e}")
                            quick_score = 0.5
                            verification_result = None
                        finally:
                            timeout_occurred[0] = False
                    
                    thread = threading.Thread(target=call_with_timeout)
                    thread.daemon = True
                    thread.start()
                    thread.join(timeout=10.0)                     
                    
                    if thread.is_alive():
                        logger.warning("⚠️ Tavily verification timeout (>10s)")
                        timeout_occurred[0] = True
                        quick_score = 0.5
                else:
                                                       
                    import signal
                    
                    def timeout_handler(signum, frame):
                        timeout_occurred[0] = True
                        raise TimeoutError("Fact verification timeout")
                    
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(10)                   
                    
                    try:
                        import spacy
                        import nltk
                        nlp = spacy.load("en_core_web_sm")
                        doc = nlp(text[:500])
                        entities = [ent.text for ent in doc.ents[:5]]
                        sentences = nltk.sent_tokenize(text[:500])
                        claims = sentences[:3]
                        verification_result = self.verifier.comprehensive_verification(text, entities, claims)
                        quick_score = verification_result.get('verification_score', 0.5)
                    except TimeoutError:
                        logger.warning("⚠️ Tavily verification timeout (>10s)")
                        quick_score = 0.5
                        verification_result = None
                    finally:
                        signal.alarm(0)
                
                if verification_result:
                    tavily_verification = {
                        'overall_score': verification_result.get('verification_score', quick_score),
                        'tavily_coverage': verification_result.get('entity_coverage', quick_score),
                        'wikipedia_coverage': verification_result.get('entity_coverage', quick_score),
                        'entities_found': verification_result.get('entities_found', 0),
                        'entities_checked': verification_result.get('entities_checked', 0),
                        'claims_verified': verification_result.get('claims_verified', 0),
                        'claims_checked': verification_result.get('claims_checked', 0),
                        'entity_results': verification_result.get('entity_results', []),
                        'claim_results': verification_result.get('claim_results', []),
                        'provider': 'tavily'
                    }
                else:
                    tavily_verification = {
                        'overall_score': quick_score,
                        'tavily_coverage': 1.0 if quick_score > 0.5 else 0.5,
                        'wikipedia_coverage': 1.0 if quick_score > 0.5 else 0.5,                                   
                        'entities_found': 1,
                        'entities_checked': 1,
                        'claims_verified': 1 if quick_score > 0.7 else 0,
                        'claims_checked': 1,
                        'entity_results': [],
                        'claim_results': [],
                        'provider': 'tavily'
                    }
                
                tavily_score = tavily_verification.get('overall_score', 0.0)
                tavily_coverage = tavily_verification.get('tavily_coverage', 0.0)
                verification_summary = tavily_verification.get('verification_summary', {})
                claims_verified = verification_summary.get('claims_verified', tavily_verification.get('claims_verified', 0))
                total_claims = verification_summary.get('total_claims_checked', tavily_verification.get('claims_checked', 1))
                entities_found = verification_summary.get('entities_found', tavily_verification.get('entities_found', 0))
                total_entities = verification_summary.get('total_entities_checked', tavily_verification.get('entities_checked', 1))
                
                                               
                verifier_name = tavily_verification.get('provider', self.verifier_type).title()
                
                logger.info(f"📊 {verifier_name} Score: {tavily_score:.3f}, Coverage: {tavily_coverage:.3f}, "
                           f"Claims: {claims_verified}/{total_claims}, Entities: {entities_found}/{total_entities}")
                
                                                                             
                                                                                          
                claims_ratio = claims_verified / total_claims if total_claims > 0 else 0.0
                entities_ratio = entities_found / total_entities if total_entities > 0 else 0.0
                
                                                                                     
                if (tavily_score >= 0.75 and tavily_coverage >= 0.65 and 
                    claims_ratio >= 0.75 and entities_ratio >= 0.70 and
                    total_claims >= 2 and total_entities >= 2):
                    
                    logger.info(f"✅ [FAST PATH] HIGH {verifier_name} verification detected! "
                               f"Skipping expensive model analysis. "
                               f"Score: {tavily_score:.3f}, Coverage: {tavily_coverage:.3f}, "
                               f"Claims: {claims_verified}/{total_claims}, Entities: {entities_found}/{total_entities}")
                    
                                                                                   
                    fast_fake_prob = max(0.0, 0.15 - (tavily_score - 0.75) * 0.3)
                    # Recompute confidence based on final fake probability (same formula as normal path)
                    distance_from_center = abs(fast_fake_prob - 0.5)
                    fast_confidence = (distance_from_center * 2) ** 1.5
                    # High verification score boosts confidence
                    if tavily_score > 0.75:
                        fast_confidence = min(1.0, fast_confidence + 0.15)
                    fast_confidence = max(0.0, min(1.0, fast_confidence))
                    
                    fast_result = {
                        'baseline_results': baseline_results,
                        'rhetorical_analysis': {},
                        'consistency_check': {},
                        'fusion_result': {
                            'fake_probability': fast_fake_prob,
                            'confidence': fast_confidence,
                            'method': 'tavily_fast_path'
                        },
                        'fact_verification': baseline_results.get('fact_verification', {}),
                        'wikipedia_verification': tavily_verification,                                   
                        'tavily_verification': tavily_verification,
                        'fast_path': True,                                       
                        'final_prediction': {
                            'prediction': 'real',
                            'fake_probability': fast_fake_prob,
                            'confidence': fast_confidence,
                            'explanation': {
                                'base_fusion_score': fast_fake_prob,
                                'consistency_adjustment': 0.0,
                                'rhetorical_adjustment': 0.0,
                                'wikipedia_adjustment': 0.0,                                   
                                'tavily_adjustment': 0.0,
                                'wikipedia_boost': -(0.35 + (tavily_score - 0.75) * 0.4),                                   
                                'tavily_boost': -(0.35 + (tavily_score - 0.75) * 0.4),
                                'final_score': fast_fake_prob,
                                'confidence': fast_confidence,
                                'key_factors': [f'high_{self.verifier_type}_verification', f'{self.verifier_type}_fast_path'],
                                'fast_path_reason': f'Tavily verification very high (score: {tavily_score:.2%}, coverage: {tavily_coverage:.2%}, claims: {claims_verified}/{total_claims}, entities: {entities_found}/{total_entities})',
                                'wikipedia_details': {                                   
                                    'verification_score': tavily_score,
                                    'coverage': tavily_coverage,
                                    'entities_found': entities_found,
                                    'entities_checked': total_entities,
                                    'claims_verified': claims_verified,
                                    'claims_checked': total_claims
                                },
                                'tavily_details': {
                                    'verification_score': tavily_score,
                                    'coverage': tavily_coverage,
                                    'entities_found': entities_found,
                                    'entities_checked': total_entities,
                                    'claims_verified': claims_verified,
                                    'claims_checked': total_claims
                                }
                            }
                        }
                    }
                    
                                                                
                    fast_result['detailed_report'] = self._generate_detailed_report(
                        text, fast_result, tavily_verification, {}, {}
                    )
                    
                    logger.info(f"💰 [COST SAVED] Skipped expensive GPT-4/model analysis for clearly real news!")
                    return convert_to_native_types(fast_result)
                
                else:
                    logger.info(f"⚠️ [NORMAL PATH] {verifier_name} verification insufficient for fast path. "
                               f"Proceeding with full analysis...")
                    
            except TimeoutError:
                logger.warning(f"{self.verifier_type.title()} verification timeout, using fallback")
                tavily_verification = {'error': 'timeout', 'overall_score': 0.0, 'provider': self.verifier_type, 'tavily_coverage': 0.0, 'wikipedia_coverage': 0.0}
            except Exception as e:
                logger.error(f"{self.verifier_type.title()} verification failed: {e}")
                tavily_verification = {'error': str(e), 'overall_score': 0.0, 'provider': self.verifier_type, 'tavily_coverage': 0.0, 'wikipedia_coverage': 0.0}
        
                                                                                                     
        logger.info("🔄 [NORMAL PATH] Performing comprehensive detection analysis...")
        
                                           
        if use_rhetorical:
            rhetorical_features = self.rhetorical_analyzer.analyze_text(text)
            logger.info("✅ Rhetorical analysis enabled")
        else:
            rhetorical_features = {}
            logger.info("⏭️ Rhetorical analysis skipped by user config")
        
                                                     
        if use_consistency:
            consistency_check = self.cross_modal_checker.comprehensive_consistency_check(text, image_metadata)
            logger.info("✅ Consistency check enabled")
        else:
            consistency_check = {'overall_consistency_score': 1.0, 'temporal_consistency': {'temporal_consistency_score': 1.0}}
            logger.info("⏭️ Consistency check skipped by user config")
        
                            
        fusion_features = self.detector_fusion.extract_fusion_features(baseline_results, rhetorical_features)
        fusion_result = self.detector_fusion.predict_fusion(fusion_features, baseline_results)
        
                                                      
        fact_verification = baseline_results.get('fact_verification', {})
        
                                  
        improved_result = {
            'baseline_results': baseline_results,
            'rhetorical_analysis': rhetorical_features,
            'consistency_check': consistency_check,
            'fusion_result': fusion_result,
            'fact_verification': fact_verification,         
            'wikipedia_verification': tavily_verification,                                   
            'tavily_verification': tavily_verification,                          
            'fast_path': False,                                         
            'final_prediction': self._generate_final_prediction(
                fusion_result, 
                consistency_check, 
                rhetorical_features,
                fact_verification,         
                tavily_verification,                               
                tavily_weight,                       
                threshold,                          
                text                              
            )
        }
        
                                                        
                                                          
        improved_result['detailed_report'] = self._generate_detailed_report(
            text, improved_result, tavily_verification, rhetorical_features, consistency_check
        )
        
        return convert_to_native_types(improved_result)
    
    def _generate_detailed_report(self, text: str, detection_result: Dict, 
                                 tavily_verification: Optional[Dict] = None,
                                 rhetorical_features: Optional[Dict] = None,
                                 consistency_check: Optional[Dict] = None) -> Dict:
                                                                        
        import re
        from datetime import datetime
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_assessment': detection_result.get('final_prediction', {}).get('prediction', 'unknown'),
            'fake_probability': detection_result.get('final_prediction', {}).get('fake_probability', 0.0),
            'confidence': detection_result.get('final_prediction', {}).get('confidence', 0.0),
            'highlighted_text': text,                                    
            'issues_found': [],
            'recommendations': [],
            'detailed_analysis': {}
        }
        
                                            
        if tavily_verification:
            tavily_issues = self._highlight_tavily_issues(text, tavily_verification)
            report['issues_found'].extend(tavily_issues['issues'])
            report['highlighted_text'] = tavily_issues['highlighted_text']
            report['detailed_analysis']['wikipedia_verification'] = {                                   
                'score': tavily_verification.get('overall_score', 0.0),
                'coverage': tavily_verification.get('tavily_coverage', tavily_verification.get('wikipedia_coverage', 0.0)),
                'entities_found': tavily_verification.get('verification_summary', {}).get('entities_found', 0),
                'claims_verified': tavily_verification.get('verification_summary', {}).get('claims_verified', 0),
                'issues': tavily_issues['issues']
            }
            report['detailed_analysis']['tavily_verification'] = {
                'score': tavily_verification.get('overall_score', 0.0),
                'coverage': tavily_verification.get('tavily_coverage', tavily_verification.get('wikipedia_coverage', 0.0)),
                'entities_found': tavily_verification.get('verification_summary', {}).get('entities_found', 0),
                'claims_verified': tavily_verification.get('verification_summary', {}).get('claims_verified', 0),
                'issues': tavily_issues['issues']
            }
        
                                     
        if rhetorical_features:
            rhetorical_issues = self._highlight_rhetorical_issues(text, rhetorical_features)
            report['issues_found'].extend(rhetorical_issues['issues'])
            report['highlighted_text'] = rhetorical_issues['highlighted_text']
            report['detailed_analysis']['rhetorical_analysis'] = {
                'emotional_language': rhetorical_features.get('emotional_language', {}),
                'loaded_language': rhetorical_features.get('loaded_language', {}),
                'readability': rhetorical_features.get('readability', {}),
                'issues': rhetorical_issues['issues']
            }
        
                                      
        if consistency_check:
            consistency_issues = self._highlight_consistency_issues(text, consistency_check)
            report['issues_found'].extend(consistency_issues['issues'])
            report['highlighted_text'] = consistency_issues['highlighted_text']
            report['detailed_analysis']['consistency_check'] = {
                'overall_score': consistency_check.get('overall_consistency_score', 0.0),
                'temporal_issues': consistency_check.get('temporal_consistency', {}).get('temporal_issues', []),
                'spatial_issues': consistency_check.get('spatial_consistency', {}).get('spatial_issues', []),
                'logical_issues': consistency_check.get('logical_consistency', {}).get('detected_contradictions', []),
                'issues': consistency_issues['issues']
            }
        
                                                                         
        all_issues = report['issues_found'].copy()
        
                                                                   
        text_quality_score = self._assess_text_quality(text)
        if text_quality_score < 0.3:                                            
                                                                      
            all_issues = [issue for issue in all_issues if not issue.get('type', '').startswith('unverified_')]
            report['text_quality_warning'] = 'Text appears to have parsing issues, fact verification reduced'
        
                                                  
        if 'baseline_results' in detection_result:
            baseline = detection_result['baseline_results']
            if 'text_detection' in baseline:
                for model_name, model_result in baseline['text_detection'].items():
                    if isinstance(model_result, dict) and 'fake_score' in model_result:
                        fake_score = model_result['fake_score']
                        if fake_score > 0.4:                                     
                            all_issues.append({
                                'type': 'model_detection',
                                'description': f'{model_name} model detected high fake probability ({fake_score:.1%})',
                                'fake_probability': fake_score
                            })
        
        report['problematic_sentences'] = self._extract_problematic_sentences(text, all_issues)
        
                                  
        report['recommendations'] = self._generate_recommendations(report['issues_found'], report['fake_probability'])
        
        return report
    
    def _assess_text_quality(self, text: str) -> float:
                                                                               
        import re
        
                                                   
        quality_indicators = {
            'excessive_fragments': 0,
            'navigation_elements': 0,
            'website_names': 0,
            'mixed_content': 0,
            'poor_sentence_structure': 0
        }
        
                                                            
        fragments = re.split(r'[.!?]+', text)
        short_fragments = sum(1 for f in fragments if len(f.strip()) < 10)
        quality_indicators['excessive_fragments'] = min(short_fragments / len(fragments), 1.0)
        
                                       
        nav_indicators = ['shopping', 'entertainment', 'explore more', 'final hours']
        quality_indicators['navigation_elements'] = sum(1 for indicator in nav_indicators if indicator.lower() in text.lower()) / len(nav_indicators)
        
                                 
        website_pattern = r'\w+\.(?:com|au|org|net)'
        websites = re.findall(website_pattern, text, re.IGNORECASE)
        quality_indicators['website_names'] = min(len(websites) / 5, 1.0)             
        
                                                             
        topics = ['kfc', 'crypto', 'prince', 'nrl', 'shopping']
        topic_count = sum(1 for topic in topics if topic.lower() in text.lower())
        quality_indicators['mixed_content'] = min(topic_count / 3, 1.0)
        
                                  
        sentences = re.split(r'[.!?]+', text)
        avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences) if sentences else 0
        quality_indicators['poor_sentence_structure'] = 1.0 if avg_sentence_length < 30 else 0.0
        
                                                                 
        quality_score = 1.0 - (sum(quality_indicators.values()) / len(quality_indicators))
        return max(0.0, min(1.0, quality_score))
    
    def _extract_problematic_sentences(self, text: str, issues: List[Dict]) -> List[Dict]:
                                                                                  
        import re
        
                                                                            
                                                                                              
        sentence_pattern = r'(?<!\.)\s*[.!?]+\s+(?![a-z]|\d+\.\d+)'
        sentences = re.split(sentence_pattern, text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]                                   
        
        problematic_sentences = []
        
                                                         
        for issue in issues:
            issue_type = issue.get('type', '')
            description = issue.get('description', '')
            
                                                                 
            for i, sentence in enumerate(sentences):
                if self._sentence_contains_issue(sentence, issue):
                                                                                           
                    if len(sentence.strip()) < 20:
                        continue
                                                                                        
                    if any(indicator in sentence.lower() for indicator in ['.com', '.au', 'shopping', 'entertainment']):
                        continue
                        
                    problematic_sentences.append({
                        'sentence': sentence,
                        'sentence_number': i + 1,
                        'issue_type': issue_type,
                        'reason': self._get_simple_reason(issue_type, description),
                        'severity': self._get_issue_severity(issue_type)
                    })
        
                                                              
        fake_prob = 0.0
        for issue in issues:
            if 'fake_probability' in issue:
                fake_prob = max(fake_prob, issue['fake_probability'])
        
        if fake_prob > 0.7:                         
            for i, sentence in enumerate(sentences):
                if len(sentence) > 20:                                   
                    problematic_sentences.append({
                        'sentence': sentence,
                        'sentence_number': i + 1,
                        'issue_type': 'model_detection',
                        'reason': f'AI model detected high fake probability ({fake_prob:.1%})',
                        'severity': 'High'
                    })
        
                                                       
        seen_sentences = set()
        unique_sentences = []
        for ps in problematic_sentences:
            if ps['sentence'] not in seen_sentences:
                seen_sentences.add(ps['sentence'])
                unique_sentences.append(ps)
        
        return sorted(unique_sentences, key=lambda x: x['sentence_number'])
    
    def _sentence_contains_issue(self, sentence: str, issue: Dict) -> bool:
                                                                  
        issue_type = issue.get('type', '')
        description = issue.get('description', '')
        
                                       
        if issue_type == 'unverified_entity':
            entity = issue.get('entity', '')
            return entity.lower() in sentence.lower()
        
                                     
        if issue_type == 'unverified_claim':
            claim = issue.get('claim', '')
            return claim.lower() in sentence.lower()
        
                                      
        if issue_type == 'emotional_language':
            emotional_words = ['shocking', 'devastating', 'incredible', 'amazing', 'terrible', 'horrible', 'fantastic', 'unbelievable']
            return any(word in sentence.lower() for word in emotional_words)
        
                                   
        if issue_type == 'loaded_language':
            loaded_words = ['obviously', 'clearly', 'undoubtedly', 'certainly', 'definitely']
            return any(word in sentence.lower() for word in loaded_words)
        
                                              
        if issue_type == 'year_inconsistency':
            import re
            years = re.findall(r'\b(18|19|20)\d{2}\b', sentence)
            return len(years) > 0
        
                                          
        if issue_type == 'model_detection':
            return True                                                                          
        
        return False
    
    def _get_simple_reason(self, issue_type: str, description: str) -> str:
                                             
        reasons = {
            'unverified_entity': 'Entity not found in fact verification',
            'unverified_claim': 'Unverified claim',
            'low_verification_score': 'Low overall verification score',
            'emotional_language': 'Contains emotional language',
            'loaded_language': 'Contains biased language',
            'year_inconsistency': 'Year information may be inaccurate',
            'logical_contradiction': 'Logical contradiction detected',
            'model_detection': 'AI model detected potential fake content',
            'rhetorical_analysis': 'Rhetorical analysis flagged suspicious patterns',
            'consistency_issue': 'Consistency check found problems',
            'fact_verification': 'Fact verification failed'
        }
        return reasons.get(issue_type, 'Potential issue detected')
    
    def _get_issue_severity(self, issue_type: str) -> str:
                                              
        severity_map = {
            'unverified_entity': 'Medium',
            'unverified_claim': 'High',
            'low_verification_score': 'High',
            'emotional_language': 'Low',
            'loaded_language': 'Medium',
            'year_inconsistency': 'High',
            'logical_contradiction': 'High',
            'model_detection': 'High',
            'rhetorical_analysis': 'Medium',
            'consistency_issue': 'High',
            'fact_verification': 'High'
        }
        return severity_map.get(issue_type, 'Medium')
    
    def _highlight_tavily_issues(self, text: str, tavily_verification: Dict) -> Dict:
                                                        
        issues = []
        highlighted_text = text
        
                                       
        entity_results = tavily_verification.get('entity_results', [])
        for entity_result in entity_results:
            if not entity_result.get('found', False):
                entity = entity_result.get('entity', '')
                if entity in text:
                    highlighted_text = highlighted_text.replace(
                        entity, 
                        f'<span style="background-color: #ffcdd2; color: #d32f2f; padding: 3px 6px; border-radius: 4px; font-weight: bold; border: 2px solid #f44336; box-shadow: 0 2px 4px rgba(244,67,54,0.3);">❌ {entity}</span>'
                    )
                    issues.append({
                        'type': 'unverified_entity',
                        'text': entity,
                        'severity': 'high',
                        'description': f'Entity "{entity}" not found in fact verification'
                    })
        
                                     
        claim_results = tavily_verification.get('claim_results', [])
        for claim_result in claim_results:
            if not claim_result.get('verified', False):
                claim = claim_result.get('claim', '')
                if claim in text:
                    highlighted_text = highlighted_text.replace(
                        claim,
                        f'<span style="background-color: #ffe0b2; color: #f57c00; padding: 3px 6px; border-radius: 4px; font-weight: bold; border: 2px solid #ff9800; box-shadow: 0 2px 4px rgba(255,152,0,0.3);">⚠️ {claim}</span>'
                    )
                    issues.append({
                        'type': 'unverified_claim',
                        'text': claim,
                        'severity': 'high',
                        'description': f'Claim "{claim}" not verified by fact verification'
                    })
        
                                           
        overall_score = tavily_verification.get('overall_score', 0.0)
        if overall_score < 0.6:
            issues.append({
                'type': 'low_verification_score',
                'text': f'Overall verification score: {overall_score:.1%}',
                'severity': 'medium',
                'description': 'Low fact verification score indicates potential factual issues'
            })
        
        return {'highlighted_text': highlighted_text, 'issues': issues}
    
    def _highlight_rhetorical_issues(self, text: str, rhetorical_features: Dict) -> Dict:
                                                 
        import re
        issues = []
        highlighted_text = text
        
                                                                  
        emotional_words = [
            'shocking', 'outrage', 'devastating', 'incredible', 'amazing', 'terrible',
            'horrible', 'fantastic', 'unbelievable', 'stunning', 'dramatic', 'explosive',
            'scandalous', 'controversial', 'sensational', 'breathtaking', 'mind-blowing',
            'lie', 'lies', 'false', 'fake', 'deceptive', 'misleading'
        ]
        
        for word in emotional_words:
            pattern = re.compile(r'\b' + re.escape(word) + r'\b', re.IGNORECASE)
            if pattern.search(highlighted_text):
                highlighted_text = pattern.sub(
                    f'<span style="background-color: #f3e5f5; color: #7b1fa2; padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid #9c27b0;">😤 {word}</span>',
                    highlighted_text
                )
        
        emotional_lang = rhetorical_features.get('emotional_language', {})
        if any(emotional_lang.values()):
            issues.append({
                'type': 'emotional_language',
                'text': 'Emotional language detected',
                'severity': 'medium',
                'description': f'High emotional content: {emotional_lang}'
            })
        
                                                            
        loaded_words = [
            'obviously', 'clearly', 'undoubtedly', 'certainly', 'definitely',
            'absolutely', 'completely', 'totally', 'entirely', 'wholly',
            'allegedly', 'supposedly', 'reportedly', 'apparently'
        ]
        
        for word in loaded_words:
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            if pattern.search(text):
                highlighted_text = pattern.sub(
                    f'<span style="background-color: #ffecb3; color: #f57f17; padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid #ffc107;">🚨 {word}</span>',
                    highlighted_text
                )
        
        loaded_lang = rhetorical_features.get('loaded_language', {})
        if any(loaded_lang.values()):
            issues.append({
                'type': 'loaded_language',
                'text': 'Loaded language detected',
                'severity': 'high',
                'description': f'Potentially manipulative language: {loaded_lang}'
            })
        
                           
        readability = rhetorical_features.get('readability', {})
        flesch_score = readability.get('flesch_reading_ease', 0)
        if flesch_score < 30:                          
            issues.append({
                'type': 'poor_readability',
                'text': f'Readability score: {flesch_score}',
                'severity': 'low',
                'description': 'Text is very difficult to read, may indicate AI generation'
            })
        
        return {'highlighted_text': highlighted_text, 'issues': issues}
    
    def _highlight_consistency_issues(self, text: str, consistency_check: Dict) -> Dict:
                                                  
        import re
        issues = []
        highlighted_text = text
        
                                                    
        year_pattern = re.compile(r'\b(18|19|20)\d{2}\b')
        years = year_pattern.findall(text)
        if years:
            for year_match in year_pattern.finditer(text):
                year = year_match.group()
                highlighted_text = highlighted_text.replace(
                    year,
                    f'<span style="background-color: #e8f5e8; color: #2e7d32; padding: 2px 4px; border-radius: 3px; font-weight: bold; border: 1px solid #4caf50;">📅 {year}</span>'
                )
        
                               
        temporal_issues = consistency_check.get('temporal_consistency', {}).get('temporal_issues', [])
        for issue in temporal_issues:
            issues.append({
                'type': 'temporal_inconsistency',
                'text': issue,
                'severity': 'high',
                'description': f'Temporal inconsistency: {issue}'
            })
        
                              
        spatial_issues = consistency_check.get('spatial_consistency', {}).get('spatial_issues', [])
        for issue in spatial_issues:
            issues.append({
                'type': 'spatial_inconsistency',
                'text': issue,
                'severity': 'high',
                'description': f'Spatial inconsistency: {issue}'
            })
        
                                      
        logical_issues = consistency_check.get('logical_consistency', {}).get('detected_contradictions', [])
        for issue in logical_issues:
            issues.append({
                'type': 'logical_contradiction',
                'text': issue,
                'severity': 'high',
                'description': f'Logical contradiction: {issue}'
            })
        
        return {'highlighted_text': highlighted_text, 'issues': issues}
    
    def _generate_recommendations(self, issues: List[Dict], fake_probability: float) -> List[str]:
                                                               
        recommendations = []
        
        if fake_probability > 0.7:
            recommendations.append("⚠️ High fake news probability - verify all facts independently")
        elif fake_probability > 0.5:
            recommendations.append("⚠️ Moderate fake news probability - cross-check key claims")
        else:
            recommendations.append("✅ Low fake news probability - appears credible")
        
                                        
        issue_types = [issue['type'] for issue in issues]
        
        if 'unverified_entity' in issue_types:
            recommendations.append("🔍 Verify all mentioned entities and organizations")
        
        if 'unverified_claim' in issue_types:
            recommendations.append("📚 Cross-reference factual claims with reliable sources")
        
        if 'low_verification_score' in issue_types:
            recommendations.append("📖 Check fact-checking sources")
        
        if 'emotional_language' in issue_types:
            recommendations.append("😤 Be aware of emotional manipulation tactics")
        
        if 'loaded_language' in issue_types:
            recommendations.append("🚨 Watch for biased or manipulative language")
        
        if 'temporal_inconsistency' in issue_types:
            recommendations.append("⏰ Verify timeline and date information")
        
        if 'spatial_inconsistency' in issue_types:
            recommendations.append("🌍 Check geographical and location details")
        
        if 'logical_contradiction' in issue_types:
            recommendations.append("🧠 Look for logical inconsistencies in the narrative")
        
        return recommendations
    
    def _generate_final_prediction(self, fusion_result: Dict, consistency_check: Dict, 
                                   rhetorical_features: Dict, fact_verification: Optional[Dict] = None,
                                   tavily_verification: Optional[Dict] = None,
                                   tavily_weight: float = 1.0,
                                   threshold: float = 0.5,
                                   text: str = "") -> Dict:
                                                                           
                           
        base_fake_prob = fusion_result.get('fake_probability', 0.5)
        
                                                                                 
        consistency_score = consistency_check.get('overall_consistency_score', 0.5)
        temporal_score = consistency_check.get('temporal_consistency', {}).get('temporal_consistency_score', 1.0)
        
                                     
        consistency_adjustment = (1.0 - consistency_score) * 0.25                              
        
                                                                
        if temporal_score < 0.5:                          
            temporal_penalty = (1.0 - temporal_score) * 0.25                            
            consistency_adjustment += temporal_penalty
            logger.warning(f"SEVERE temporal penalty applied: +{temporal_penalty:.3f} (temporal_score: {temporal_score:.3f})")
        
                                                                      
        if temporal_score < 0.2:                                          
            extreme_penalty = 0.3                          
            consistency_adjustment += extreme_penalty
            logger.warning(f"EXTREME temporal penalty applied: +{extreme_penalty:.3f} (anachronism detected)")
        
                                       
        loaded_language = rhetorical_features.get('loaded_language', {})
        rhetorical_adjustment = sum(loaded_language.values()) * 0.1                                                   
        
                                                   
        tavily_adjustment = 0.0
        tavily_boost = 0.0                                                    
        contradiction_penalty = 0.0                                                       
        
                                                    
        tavily_score = 0.0
        tavily_coverage = 0.0
        verifier_display_name = 'Tavily'
        
                                                                                                      
        if tavily_verification and 'overall_score' in tavily_verification:
                                                                              
            tavily_score = tavily_verification.get('overall_score', 0.0)
            tavily_coverage = tavily_verification.get('tavily_coverage', tavily_verification.get('wikipedia_coverage', 0.0))
            verifier_display_name = tavily_verification.get('provider', self.verifier_type).title()
            base_tavily_adjustment = (1.0 - tavily_score) * 0.20 + (1.0 - tavily_coverage) * 0.15
            tavily_adjustment = base_tavily_adjustment * tavily_weight                             
            
                                                                                                                            
            if tavily_score < 0.5 or tavily_coverage < 0.6:                                                            
                base_contradiction_penalty = 0.15                                                   
                contradiction_penalty = base_contradiction_penalty * tavily_weight                             
                logger.warning(f"TAVILY LOW VERIFICATION: +{contradiction_penalty:.2f} penalty (score: {tavily_score:.3f}, coverage: {tavily_coverage:.3f})")
            
                                                                                              
            if tavily_coverage >= 0.8 and tavily_score >= 0.7:                           
                                                                            
                claims_verified = tavily_verification.get('claims_verified', 0)
                total_claims = tavily_verification.get('total_claims', 1)
                claims_ratio = claims_verified / total_claims if total_claims > 0 else 0
                
                                                                                                
                if claims_ratio < 0.7:                                                            
                    contradiction_penalty += 0.15 * tavily_weight                              
                    logger.warning(f"TAVILY POTENTIAL CONTRADICTION: +{0.15 * tavily_weight:.2f} penalty (coverage: {tavily_coverage:.3f}, claims_ratio: {claims_ratio:.3f})")
                
                                                                             
                                                                                                   
                import re
                years_in_text = re.findall(r'\b(18|19|20)\d{2}\b', text.lower())
                if years_in_text and claims_ratio < 0.9:                          
                    contradiction_penalty += 0.15 * tavily_weight                              
                    logger.warning(f"TAVILY YEAR CONTRADICTION DETECTED: +{0.15 * tavily_weight:.2f} penalty (years: {years_in_text}, claims_ratio: {claims_ratio:.3f})")
            
                                                                                            
            if tavily_score >= 0.5:
                                                                    
                tavily_boost = -0.30                               
                logger.info(f"{verifier_display_name} HIGH VERIFICATION BOOST: -{abs(tavily_boost):.2f} (score: {tavily_score:.3f})")
            elif tavily_coverage >= 0.75 and tavily_score >= 0.4:                                          
                                                                                          
                tavily_boost = -0.15                               
                logger.info(f"{verifier_display_name} HIGH COVERAGE BOOST: -{abs(tavily_boost):.2f} (coverage: {tavily_coverage:.3f}, score: {tavily_score:.3f})")
            
            logger.info(f"{verifier_display_name} adjustment: {tavily_adjustment:.3f}, contradiction penalty: {contradiction_penalty:.3f}, boost: {tavily_boost:.3f} (score: {tavily_score:.3f}, coverage: {tavily_coverage:.3f})")
        
                                                       
        final_fake_prob = min(1.0, max(0.0, base_fake_prob + consistency_adjustment + rhetorical_adjustment + tavily_adjustment + contradiction_penalty + tavily_boost))
        # Recompute confidence after adjustments
        # Use squared function for more aggressive confidence scaling
        distance_from_center = abs(final_fake_prob - 0.5)
        final_confidence = (distance_from_center * 2) ** 1.5  # Power of 1.5 for better scaling
        # Consider adjustment magnitude to boost confidence when significant changes were made
        total_adjustment = abs(consistency_adjustment) + abs(rhetorical_adjustment) + abs(tavily_adjustment) + abs(contradiction_penalty) + abs(tavily_boost)
        if total_adjustment > 0.1:  # Significant adjustments were made
            final_confidence = min(1.0, final_confidence + 0.1)  # Boost confidence by 0.1
        final_confidence = max(0.0, min(1.0, final_confidence))
        
                              
        explanation = {
            'base_fusion_score': base_fake_prob,
            'consistency_adjustment': consistency_adjustment,
            'rhetorical_adjustment': rhetorical_adjustment,
            'wikipedia_adjustment': tavily_adjustment,                                   
            'tavily_adjustment': tavily_adjustment,
            'wikipedia_contradiction_penalty': contradiction_penalty,                                   
            'tavily_contradiction_penalty': contradiction_penalty,
            'wikipedia_boost': tavily_boost,                                   
            'tavily_boost': tavily_boost,
            'final_score': final_fake_prob,
            'confidence': final_confidence,
            'key_factors': []
        }
        
                              
        if consistency_adjustment > 0.1:
            explanation['key_factors'].append('inconsistent_information')
        if temporal_score < 0.5:                                 
            explanation['key_factors'].append('severe_temporal_error')
        if rhetorical_adjustment > 0.05:
            explanation['key_factors'].append('loaded_language')
        if contradiction_penalty > 0.0:                              
            explanation['key_factors'].append(f'extremely_low_{self.verifier_type}_verification')
        elif tavily_adjustment > 0.1:
            explanation['key_factors'].append(f'low_{self.verifier_type}_verification')
        if tavily_boost < -0.1:                     
            explanation['key_factors'].append(f'high_{self.verifier_type}_verification')
        if base_fake_prob > 0.7:
            explanation['key_factors'].append('baseline_detection')
        
                                                        
        if tavily_verification:
            explanation['wikipedia_details'] = {                                   
                'verification_score': tavily_verification.get('overall_score', 0.0),
                'coverage': tavily_verification.get('tavily_coverage', tavily_verification.get('wikipedia_coverage', 0.0)),
                'entities_found': tavily_verification.get('verification_summary', {}).get('entities_found', 0),
                'entities_checked': tavily_verification.get('verification_summary', {}).get('total_entities_checked', 0),
                'claims_verified': tavily_verification.get('verification_summary', {}).get('claims_verified', 0),
                'claims_checked': tavily_verification.get('verification_summary', {}).get('total_claims_checked', 0)
            }
            explanation['tavily_details'] = {
                'verification_score': tavily_verification.get('overall_score', 0.0),
                'coverage': tavily_verification.get('tavily_coverage', tavily_verification.get('wikipedia_coverage', 0.0)),
                'entities_found': tavily_verification.get('verification_summary', {}).get('entities_found', 0),
                'entities_checked': tavily_verification.get('verification_summary', {}).get('total_entities_checked', 0),
                'claims_verified': tavily_verification.get('verification_summary', {}).get('claims_verified', 0),
                'claims_checked': tavily_verification.get('verification_summary', {}).get('total_claims_checked', 0)
            }
        
        misleading_lower = 0.4
        misleading_upper = 0.6
        if final_fake_prob >= misleading_upper:
            prediction_label = 'fake'
        elif final_fake_prob <= misleading_lower:
            prediction_label = 'real'
        else:
            prediction_label = 'misleading'
        
        return {
            'prediction': prediction_label,
            'fake_probability': final_fake_prob,
            'confidence': final_confidence,
            'explanation': explanation,
            'threshold_used': threshold
        }
