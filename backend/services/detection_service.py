"""
Detection Service - Unified Detection Module
Integrates GPT-4, RoBERTa, CLIP, Zero-Shot, and Fact Verification
"""
# Print config at module load time
import os as _os
print(f"[MODULE LOAD] detection_service.py")
print(f"[MODULE LOAD] OPENAI_API_KEY from env: {bool(_os.getenv('OPENAI_API_KEY'))}")
print(f"[MODULE LOAD] API_PROVIDER from env: {_os.getenv('API_PROVIDER', 'not set')}")

from typing import Dict, List, Optional, Tuple, Any
import torch
import torch.nn.functional as F
from transformers import (
    pipeline,
    CLIPProcessor,
    CLIPModel
)
from PIL import Image
import numpy as np
import requests
import io
import base64
import openai
from openai import OpenAI
from config import Config
import re
from collections import defaultdict
import spacy

def convert_to_native_types(obj: Any) -> Any:
    """Recursively convert numpy and torch types to Python native types"""
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


class DetectionService:
    """Unified detection service with GPT-4, traditional models, and fact verification"""
    
    def __init__(self):
        self.models = {}
        self.gpt4_client = None
        self.nlp = None  # spaCy for fact verification
        self._load_models()
        self._initialize_gpt4()
        self._initialize_spacy()
    
    def _load_models(self):
        """Load traditional detection models with graceful degradation"""
        print("Loading detection models...")
        
        # RoBERTa for text classification
        try:
            self.models['roberta'] = pipeline(
                "text-classification",
                model="roberta-base",
                return_all_scores=True
            )
            print("✅ RoBERTa model loaded successfully")
        except Exception as e:
            print(f"⚠️ Warning: RoBERTa model failed to load: {e}")
            self.models['roberta'] = None
        
        # CLIP for multimodal detection
        try:
            self.models['clip_processor'] = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            self.models['clip_model'] = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            print("✅ CLIP model loaded successfully")
        except Exception as e:
            print(f"⚠️ Warning: CLIP model failed to load: {e}")
            self.models['clip_processor'] = None
            self.models['clip_model'] = None
        
        # Zero-shot classifier
        try:
            self.models['zero_shot'] = pipeline(
                "zero-shot-classification",
                model="facebook/bart-large-mnli"
            )
            print("✅ Zero-shot model loaded successfully")
        except Exception as e:
            print(f"⚠️ Warning: Zero-shot model failed to load: {e}")
            self.models['zero_shot'] = None
        
        print("All detection models loaded successfully!")
    
    def _initialize_gpt4(self):
        """Initialize GPT-4 client"""
        # Force reload config from environment
        import os
        api_key = os.getenv("OPENAI_API_KEY") or Config.OPENAI_API_KEY
        self.gpt4_model = Config.DEFAULT_GPT_MODEL
        
        print(f"[DEBUG] API Provider: openai")
        print(f"[DEBUG] API Key exists: {bool(api_key)}")
        print(f"[DEBUG] API Key prefix: {api_key[:20] if api_key else 'None'}...")
        
        if api_key:
            try:
                self.gpt4_client = openai.OpenAI(api_key=api_key)
                
                print(f"✅ GPT-4 detector initialized with OpenAI ({self.gpt4_model})")
            except Exception as e:
                print(f"❌ Error initializing GPT-4: {e}")
                self.gpt4_client = None
        else:
            print(f"⚠️ Warning: No OpenAI API key. GPT-4 detection disabled.")
    
    def _initialize_spacy(self):
        """Initialize spaCy for fact verification"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print("Warning: spaCy model not found. Fact verification will be limited.")
            self.nlp = None
    
    # ==================== Traditional Detection Methods ====================
    
    def roberta_detection(self, text: str) -> Dict:
        """RoBERTa-based fake news detection"""
        if self.models['roberta'] is None:
            return {
                'model': 'roberta',
                'fake_score': 0.5,
                'real_score': 0.5,
                'prediction': 'skipped',
                'confidence': 0.0,
                'status': 'model_not_loaded'
            }
        
        try:
            roberta_pipeline = self.models['roberta']
            results = roberta_pipeline(text[:512])[0]
            
            fake_score = next((r['score'] for r in results if r['label'] == 'LABEL_1'), 0.5)
            real_score = next((r['score'] for r in results if r['label'] == 'LABEL_0'), 0.5)
            
            return {
                'model': 'roberta',
                'fake_score': fake_score,
                'real_score': real_score,
                'prediction': 'fake' if fake_score > real_score else 'real',
                'confidence': max(fake_score, real_score)
            }
        except Exception as e:
            return {'error': str(e), 'model': 'roberta'}
    
    def zero_shot_detection(self, text: str) -> Dict:
        """Zero-shot classification"""
        if self.models['zero_shot'] is None:
            return {
                'model': 'zero_shot',
                'prediction': 'skipped',
                'confidence': 0.0,
                'status': 'model_not_loaded'
            }
        
        try:
            zero_shot_pipeline = self.models['zero_shot']
            result = zero_shot_pipeline(
                text[:512],
                candidate_labels=['real news', 'fake news', 'misleading']
            )
            
            labels = result['labels']
            scores = result['scores']
            
            fake_score = scores[labels.index('fake news')] if 'fake news' in labels else 0.5
            real_score = scores[labels.index('real news')] if 'real news' in labels else 0.5
            
            return {
                'model': 'zero_shot',
                'fake_score': fake_score,
                'real_score': real_score,
                'prediction': labels[0],
                'confidence': scores[0]
            }
        except Exception as e:
            return {'error': str(e), 'model': 'zero_shot'}
    
    def clip_multimodal_detection(self, text: str, image_url_or_b64: str) -> Dict:
        """CLIP-based image-text consistency check"""
        if self.models['clip_processor'] is None or self.models['clip_model'] is None:
            return {
                'model': 'clip',
                'text_image_similarity': 0.5,
                'is_consistent': True,
                'consistency_score': 0.5,
                'status': 'model_not_loaded'
            }
        
        try:
            processor = self.models['clip_processor']
            model = self.models['clip_model']
            
            # Load image
            if image_url_or_b64.startswith('http'):
                response = requests.get(image_url_or_b64)
                image = Image.open(io.BytesIO(response.content))
            else:
                image_data = base64.b64decode(image_url_or_b64.split(',')[1] if ',' in image_url_or_b64 else image_url_or_b64)
                image = Image.open(io.BytesIO(image_data))
            
            # CLIP processing
            inputs = processor(text=[text[:77]], images=image, return_tensors="pt", padding=True)
            outputs = model(**inputs)
            
            logits_per_image = outputs.logits_per_image
            similarity = torch.sigmoid(logits_per_image).item()
                
            return {
                    'model': 'clip',
                    'text_image_similarity': similarity,
                'is_consistent': similarity > 0.5,
                'consistency_score': similarity
                }
        except Exception as e:
            return {'error': str(e), 'model': 'clip'}
    
    # ==================== GPT-4 Detection Methods ====================
    
    def gpt4_detect(self, text: str, mode: str = 'full') -> Dict:
        """GPT-4-based fake news detection"""
        if not self.gpt4_client:
            return {
                'error': 'GPT-4 not initialized',
                'fake_probability': 0.5,
                'method': 'gpt4_unavailable'
            }
        
        try:
            if mode == 'quick':
                return self._gpt4_quick_check(text)
            else:
                return self._gpt4_full_analysis(text)
        except Exception as e:
            print(f"GPT-4 detection error: {e}")
            return {
                'error': str(e),
                'fake_probability': 0.5,
                'method': 'gpt4_error'
            }
    
    def _gpt4_full_analysis(self, text: str) -> Dict:
        """Full GPT-4 analysis with reasoning"""
        prompt = f"""Analyze this news article for fake news indicators.

ARTICLE:
{text[:2000]}

Respond in this format:
VERDICT: [Real/Suspicious/Fake]
CONFIDENCE: [0-100]%
FAKE_PROBABILITY: [0.0-1.0]
REASONING:
- **Point 1: [Title]** - [Detailed explanation in 1-2 sentences]
- **Point 2: [Title]** - [Detailed explanation in 1-2 sentences]
- **Point 3: [Title]** - [Detailed explanation in 1-2 sentences]

Consider: factual accuracy, source credibility, language manipulation, logical consistency.
IMPORTANT: Each reasoning point MUST include both a title and a detailed explanation after the dash."""
        
        response = self.gpt4_client.chat.completions.create(
            model=self.gpt4_model,
            messages=[
                {"role": "system", "content": "You are an expert fact-checker and fake news detector."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=800
        )
        
        result_text = response.choices[0].message.content
        return self._parse_gpt4_response(result_text, 'gpt4_full')
    
    def _gpt4_quick_check(self, text: str) -> Dict:
        """Quick GPT-4 check"""
        prompt = f"""Is this news fake or real? Respond: FAKE [0.0-1.0] or REAL [0.0-1.0]

Article: {text[:1000]}"""
        
        response = self.gpt4_client.chat.completions.create(
            model=self.gpt4_model,
            messages=[
                {"role": "system", "content": "You are a fake news detector. Be concise."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        result_text = response.choices[0].message.content.lower()
        
        if 'fake' in result_text:
            match = re.search(r'(\d+\.?\d*)', result_text)
            if match:
                prob = float(match.group(1))
                if prob <= 1.0:
                    return {'fake_probability': prob, 'method': 'gpt4_quick'}
            return {'fake_probability': 0.7, 'method': 'gpt4_quick'}
        else:
            return {'fake_probability': 0.3, 'method': 'gpt4_quick'}
    
    def _parse_gpt4_response(self, response: str, method: str) -> Dict:
        """Parse GPT-4 response"""
        fake_probability = 0.5
        confidence = 0.5
        verdict = "unknown"
        reasoning = []
        
        for line in response.split('\n'):
            line_lower = line.lower().strip()
            
            if line_lower.startswith('verdict:'):
                verdict_text = line.split(':', 1)[1].strip().lower()
                if 'fake' in verdict_text:
                    verdict = 'fake'
                    fake_probability = 0.8
                elif 'suspicious' in verdict_text:
                    verdict = 'suspicious'
                    fake_probability = 0.6
                elif 'real' in verdict_text:
                    verdict = 'real'
                    fake_probability = 0.2
            
            elif line_lower.startswith('confidence:'):
                try:
                    conf_text = line.split(':', 1)[1].strip()
                    confidence = float(conf_text.replace('%', '').strip()) / 100.0
                except:
                    pass
            
            elif line_lower.startswith('fake_probability:'):
                try:
                    fake_probability = float(line.split(':', 1)[1].strip())
                except:
                    pass
            
            elif line.strip().startswith('-'):
                reasoning.append(line.strip()[1:].strip())
        
        return {
            'fake_probability': max(0.0, min(1.0, fake_probability)),
            'confidence': max(0.0, min(1.0, confidence)),
            'verdict': verdict,
            'reasoning': reasoning[:5],
            'method': method,
            'model': self.gpt4_model,
            'is_generated': fake_probability > 0.5,  # For compatibility
            'sensitivity': fake_probability * 10  # For compatibility
        }
    
    # ==================== Fact Verification Methods ====================
    
    def verify_facts(self, text: str) -> Dict:
        """Verify facts using Wikipedia"""
        print("Starting fact verification...")
        
        # Extract entities
        entities = self._extract_entities(text)
        
        # Verify entities
        entities_verified = []
        for person in entities.get('PERSON', [])[:3]:
            entities_verified.append(self._verify_entity(person, 'PERSON'))
        for org in entities.get('ORG', [])[:3]:
            entities_verified.append(self._verify_entity(org, 'ORG'))
        for location in entities.get('GPE', [])[:2]:
            entities_verified.append(self._verify_entity(location, 'GPE'))
        
        # Extract and verify claims
        claims = self._extract_claims(text)
        claims_verified = []
        for claim in claims[:3]:
            if len(claim.strip()) > 10:
                claims_verified.append(self._verify_claim(claim))
        
        # Calculate verification score
        fake_probability = self._calculate_verification_score(entities_verified, claims_verified)
        
        verified_entities = [e for e in entities_verified if e.get('verified', False)]
        unverified_entities = [e for e in entities_verified if not e.get('verified', False)]
        supported_claims = [c for c in claims_verified if c.get('supported', False)]
        
        return {
            'fake_probability': fake_probability,
            'verification_score': 1.0 - fake_probability,
            'entities_checked': len(entities_verified),
            'entities_verified': len(verified_entities),
            'claims_checked': len(claims_verified),
            'claims_supported': len(supported_claims),
            'verified_entities': verified_entities[:3],
            'unverified_entities': unverified_entities[:3],
            'supported_claims': supported_claims[:2],
            'method': 'wikipedia_verification'
        }
    
    def _extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities"""
        if not self.nlp:
            return {'PERSON': [], 'ORG': [], 'GPE': []}
        
        doc = self.nlp(text)
        entities = defaultdict(list)
        
        for ent in doc.ents:
            if ent.label_ in ['PERSON', 'ORG', 'GPE']:
                entities[ent.label_].append(ent.text)
        
        return dict(entities)
    
    def _extract_claims(self, text: str) -> List[str]:
        """Extract key claims"""
        claims = []
        patterns = [
            r'(?:announced|revealed|discovered|stated|confirmed)\s+(?:that\s+)?(.+?)(?:\.|$)',
            r'(?:according to|officials say|experts claim)\s+(.+?)(?:\.|$)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            claims.extend(matches[:3])
        
        return claims[:5]
    
    def _verify_entity(self, entity: str, entity_type: str) -> Dict:
        """Verify entity via Wikipedia"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': entity,
                'srlimit': 3
            }
            
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params=params,
                timeout=5
            )
            data = response.json()
            
            if 'query' in data and 'search' in data['query']:
                results = data['query']['search']
                num_results = len(results)
                
                if num_results > 0:
                    return {
                        'entity': entity,
                        'type': entity_type,
                        'verified': True,
                        'confidence': min(0.9, 0.3 + num_results * 0.2),
                        'wiki_titles': [r['title'] for r in results[:3]]
                    }
            
            return {
                'entity': entity,
                'type': entity_type,
                'verified': False,
                'confidence': 0.0,
                'reason': 'No Wikipedia entry found'
            }
        
        except Exception as e:
            return {
                'entity': entity,
                'type': entity_type,
                'verified': False,
                'confidence': 0.0,
                'error': str(e)
            }
    
    def _verify_claim(self, claim: str) -> Dict:
        """Verify claim via Wikipedia"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'list': 'search',
                'srsearch': claim,
                'srlimit': 3
            }
            
            response = requests.get(
                "https://en.wikipedia.org/w/api.php",
                params=params,
                timeout=5
            )
            data = response.json()
            
            num_results = len(data.get('query', {}).get('search', []))
            
            if num_results >= 2:
                return {'claim': claim, 'supported': True, 'confidence': 0.7, 'evidence_count': num_results}
            elif num_results == 1:
                return {'claim': claim, 'supported': True, 'confidence': 0.5, 'evidence_count': 1}
            else:
                return {'claim': claim, 'supported': False, 'confidence': 0.2, 'evidence_count': 0}
        
        except Exception as e:
            return {'claim': claim, 'supported': False, 'confidence': 0.2, 'error': str(e)}
    
    def _calculate_verification_score(self, entities_verified: List[Dict], claims_verified: List[Dict]) -> float:
        """Calculate overall verification score"""
        if not entities_verified and not claims_verified:
            return 0.5
        
        entity_score = 0.5
        if entities_verified:
            verified_count = sum(1 for e in entities_verified if e.get('verified', False))
            entity_score = verified_count / len(entities_verified)
        
        claim_score = 0.5
        if claims_verified:
            supported_count = sum(1 for c in claims_verified if c.get('supported', False))
            claim_score = supported_count / len(claims_verified)
        
        overall_score = 0.4 * entity_score + 0.6 * claim_score
        fake_probability = 1.0 - overall_score
        
        return fake_probability
    
    # ==================== Main Detection Method ====================
    
    def baseline_detection(self, text: str, image_url_or_b64: Optional[str] = None) -> Dict:
        """Unified baseline detection using all methods"""
        results = {
            'text_detection': {},
            'multimodal_detection': {},
            'fact_verification': {},
            'features': []
        }
        
        # Traditional detections
        results['text_detection']['roberta'] = self.roberta_detection(text)
        results['text_detection']['zero_shot'] = self.zero_shot_detection(text)
        
        # GPT-4 detections (replaces DetectGPT and GLTR)
        results['text_detection']['detectgpt'] = self.gpt4_detect(text, mode='full')
        results['text_detection']['gltr'] = self.gpt4_detect(text, mode='quick')
        
        # CLIP if image provided
        if image_url_or_b64:
            results['multimodal_detection']['clip'] = self.clip_multimodal_detection(text, image_url_or_b64)
        
        # Fact verification
        results['fact_verification'] = self.verify_facts(text)
        
        # Convert to native types
        return convert_to_native_types(results)
