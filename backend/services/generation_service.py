"""
Generation Service - Fake News Generation Module
Uses OpenAI GPT-4o for controlled fake news creation
"""
from typing import Dict, List, Optional
import openai
import random
import re
from datetime import datetime
from config import Config

class FakeNewsGenerator:
    """Fake news generator using OpenAI GPT models"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_provider = "openai"
        self.api_key = api_key or Config.OPENAI_API_KEY
        
        self.client = None
        self.strategies = {}
        self._initialize_client()
        self._initialize_strategies()
    
    def _initialize_client(self):
        """Initialize OpenAI client"""
        if self.api_key:
            try:
                self.client = openai.OpenAI(api_key=self.api_key)
                print(f"✅ OpenAI client initialized successfully!")
                print(f"Using model: {Config.DEFAULT_GPT_MODEL}")
            except Exception as e:
                print(f"❌ Error initializing API client: {e}")
                self.client = None
        else:
            print(f"⚠️ Warning: OpenAI API key not found. Generation service will not work.")
            self.client = None
    
    def _initialize_strategies(self):
        """Initialize generation strategies"""
        self.strategies = {
            "loaded_language": {
                "description": "Emotionally charged language in professional format",
                "prompt_template": "Write a professional news article about {topic} that includes false or exaggerated claims. Use emotional language naturally within professional reporting. Include fabricated expert quotes and fake statistics."
            },
            "conspiracy": {
                "description": "Suggest hidden agendas",
                "prompt_template": "Write a professional news article about {topic} that subtly suggests conspiracies or cover-ups. Use vague attributions and imply hidden motives."
            },
            "fabricated_evidence": {
                "description": "False statistics and fake quotes",
                "prompt_template": "Write a professional news article about {topic} with completely fabricated statistics, made-up study results, and quotes from fictional experts."
            },
            "timeline_shift": {
                "description": "Confuse timelines",
                "prompt_template": "Write a professional news article about {topic} that mixes up timelines, presents old events as recent, or creates false chronological connections."
            },
            "misleading_headlines": {
                "description": "Professional headline with misleading content",
                "prompt_template": "Write a professional news article about {topic} where the claims are exaggerated or false, but presented authoritatively."
            },
            "false_urgency": {
                "description": "Create false urgency",
                "prompt_template": "Write a professional news article about {topic} that fabricates an urgent situation that doesn't exist."
            },
            "emotional_manipulation": {
                "description": "Exploit emotions",
                "prompt_template": "Write a professional news article about {topic} using fabricated emotional stories to manipulate reader emotions."
            }
        }
    
    def generate_with_strategy(self, topic: str, strategy: str, model_type: Optional[str] = None) -> Dict:
        """Generate fake news using specified strategy"""
        if strategy not in self.strategies:
            strategy = "loaded_language"
        
        # Use GPT model
        if model_type is None:
            model_type = Config.DEFAULT_GPT_MODEL
        
        if self.client is None:
            return {
                "success": False,
                "error": "OpenAI client not initialized. Please provide API key.",
                "topic": topic,
                "strategy": strategy
            }
        
        return self._generate_with_gpt(topic, strategy, model_type)
    
    def _generate_with_gpt(self, topic: str, strategy: str, model_type: str) -> Dict:
        """Generate fake news with GPT"""
        try:
            system_prompt = """You are a professional news writer creating fake news articles for research purposes.

Your articles must:
1. Look exactly like real BBC/CNN/Reuters articles
2. Start with a professional headline (NO "SHOCKING:", "BREAKING:", "DEVASTATING:")
3. Include dateline (e.g., "PARIS - " or "SYDNEY - ")
4. Use calm, professional tone
5. Include FALSE information: fake statistics, made-up quotes, fabricated events
6. Sound completely credible but be verifiably false

Headline examples to use:
- "Study raises questions about [topic]"
- "Experts debate [topic] implications"
- "Report finds unexpected [topic] trends"
- "Analysis suggests [topic] challenges"
- "New data highlights [topic] concerns"

Vary your headlines - don't repeat the same pattern."""

            strategy_desc = self.strategies[strategy]["description"]
            prompt_template = self.strategies[strategy]["prompt_template"]
            user_prompt = prompt_template.format(topic=topic)
            
            full_prompt = f"""{user_prompt}

Requirements:
- Professional headline (vary the style)
- Dateline format
- 3-5 paragraphs
- Include fake data presented as real
- NO "SHOCKING", "BREAKING", "DEVASTATING" prefixes
- NO research disclaimers at the end
- Just write like BBC news with false information embedded

Write the article now."""

            response = self.client.chat.completions.create(
                model=model_type,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=600,
                temperature=0.5,
                top_p=0.8,
                frequency_penalty=0.7,
                presence_penalty=0.4
            )
            
            generated_text = response.choices[0].message.content.strip()
            formatted_article = self._format_article(generated_text)
            
            return {
                "success": True,
                "article": formatted_article,
                "topic": topic,
                "strategy": strategy,
                "model": model_type,
                "api_provider": self.api_provider,
                "metadata": {
                    "generation_time": datetime.now().isoformat(),
                    "word_count": len(formatted_article.split()),
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "topic": topic,
                "strategy": strategy,
                "model": model_type,
                "api_provider": self.api_provider
            }
    
    def _format_article(self, text: str) -> str:
        """Clean article to professional format"""
        # Remove all asterisks and markdown
        text = re.sub(r'\*+', '', text)
        text = re.sub(r'#+', '', text)
        
        lines = []
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                if lines and lines[-1] != '':
                    lines.append('')
                continue
            
            # Skip research disclaimers
            if re.search(r'(generated|research purposes|for research)', line, re.IGNORECASE):
                continue
            
            # Remove sensational prefixes
            line = re.sub(r'^(SHOCKING|BREAKING|DEVASTATING|URGENT|EXCLUSIVE):\s*', '', line, flags=re.IGNORECASE)
            
            lines.append(line)
        
        text = '\n'.join(lines)
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        return text.strip()
    
    def generate_multiple_samples(self, topic: str, num_samples: int = 5) -> List[Dict]:
        """Generate multiple samples"""
        samples = []
        strategies = list(self.strategies.keys())
        
        for i in range(num_samples):
            strategy = random.choice(strategies)
            result = self.generate_with_strategy(topic, strategy)
            if result.get("success"):
                samples.append(result)
        
        return samples
    
    def get_available_strategies(self) -> Dict:
        """Get available strategies"""
        return {
            strategy: {
                "name": strategy,
                "description": config["description"]
            }
            for strategy, config in self.strategies.items()
        }
    
    def get_available_models(self) -> List[str]:
        """Get available models based on provider"""
        return Config.AVAILABLE_GPT_MODELS


class GenerationService:
    """Main generation service"""
    
    def __init__(self):
        self.fake_news_generator = FakeNewsGenerator()
    
    def generate_fake_news(self, request: Dict) -> Dict:
        """Generate fake news from request"""
        topic = request.get("topic", "")
        strategy = request.get("strategy", "loaded_language")
        model_type = request.get("model_type")
        
        if not topic:
            return {
                "success": False,
                "error": "Topic is required"
            }
        
        return self.fake_news_generator.generate_with_strategy(topic, strategy, model_type)
    
    def generate_batch(self, topics: List[str], strategy: Optional[str] = None, samples_per_topic: int = 1) -> List[Dict]:
        """Generate multiple fake news articles"""
        results = []
        for topic in topics:
            if samples_per_topic > 1:
                # Generate multiple samples per topic
                topic_results = self.fake_news_generator.generate_multiple_samples(topic, samples_per_topic)
                results.extend(topic_results)
            else:
                # Generate single sample per topic
                result = self.generate_fake_news({
                    "topic": topic,
                    "strategy": strategy or "loaded_language"
                })
                results.append(result)
        return results
    
    def get_service_info(self) -> Dict:
        """Get service information"""
        return {
            "api_provider": self.fake_news_generator.api_provider,
            "available_strategies": self.fake_news_generator.get_available_strategies(),
            "available_models": self.fake_news_generator.get_available_models(),
            "client_initialized": self.fake_news_generator.client is not None,
            "requires_api_key": self.fake_news_generator.client is None
        }
