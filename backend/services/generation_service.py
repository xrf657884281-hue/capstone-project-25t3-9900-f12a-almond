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
                print(f"OpenAI client initialized successfully!")
                print(f"Using model: {Config.DEFAULT_GPT_MODEL}")
            except Exception as e:
                print(f"Error initializing OpenAI client: {e}")
                self.client = None
        else:
            print(f"Warning: OPENAI_API_KEY not found. Generation service will not work.")
            self.client = None
    
    def _initialize_strategies(self):
        """Initialize generation strategies"""
        self.strategies = {
            "loaded_language": {
                "description": "Emotionally charged language in professional format",
                "prompt_template": """Write a professional news article about {topic} using the LOADED LANGUAGE strategy.

Strategy specifics:
- Use emotionally charged but professional language (e.g., "concerns mount", "raises questions", "sparks debate")
- Present exaggerated or false claims as established facts
- Include fabricated expert quotes expressing worry or concern
- Add fake statistics showing alarming trends
- Use words like: "significant", "substantial", "considerable", "notable", "marked"
- Maintain BBC/Reuters professional tone while embedding emotional framing"""
            },
            "conspiracy": {
                "description": "Suggest hidden agendas and cover-ups",
                "prompt_template": """Write a professional news article about {topic} using the CONSPIRACY strategy.

Strategy specifics:
- Subtly suggest conspiracies or cover-ups without being obvious
- Use phrases like: "questions remain unanswered", "officials have yet to explain", "critics argue"
- Imply information is being withheld or suppressed
- Reference fake "leaked documents" or "insider sources"
- Create false connections between unrelated events or entities
- Use passive voice to create mystery (e.g., "has been observed", "was reportedly seen")
- Include fabricated expert questioning official narratives"""
            },
            "fabricated_evidence": {
                "description": "False statistics, fake studies, and made-up quotes",
                "prompt_template": """Write a professional news article about {topic} using the FABRICATED EVIDENCE strategy.

Strategy specifics:
- Include multiple completely fabricated statistics with precise numbers (e.g., "47.3%", "increased by 23.6%")
- Cite fake studies with specific names and dates (e.g., "2024 International Climate Study")
- Create fake expert names with realistic credentials and institutions
- Reference non-existent journals or publications (e.g., "published in Journal of Environmental Science")
- Include fabricated survey data with sample sizes (e.g., "surveying 3,200 participants across 15 countries")
- Add made-up conference presentations or research findings
- Use specific fake dates for when studies were conducted or published"""
            },
            "timeline_shift": {
                "description": "Confuse timelines and chronology",
                "prompt_template": """Write a professional news article about {topic} using the TIMELINE MANIPULATION strategy.

Strategy specifics:
- Present old events as if they happened recently
- Confuse the sequence of events or cause-and-effect relationships
- Use vague temporal references that mislead (e.g., "in recent months" for old events)
- Create false chronological connections between unrelated events
- Misattribute dates to studies, reports, or incidents
- Suggest false trends by manipulating time periods
- Compare incomparable time periods to show false patterns"""
            },
            "misleading_headlines": {
                "description": "Professional headline that misleads about content",
                "prompt_template": """Write a professional news article about {topic} using the MISLEADING HEADLINES strategy.

Strategy specifics:
- Create a professional headline that technically relates to {topic} but misleads
- The article content should contain exaggerated or false claims presented as authoritative facts
- Use hedging in headline (e.g., "may", "could", "suggests") but be more definitive in body
- Include fabricated data that seems to support the misleading headline
- Add fake expert quotes that align with the misleading framing
- Make false connections between the topic and unrelated concerns"""
            },
            "false_urgency": {
                "description": "Create false sense of urgency or crisis",
                "prompt_template": """Write a professional news article about {topic} using the FALSE URGENCY strategy.

Strategy specifics:
- Fabricate an urgent situation, crisis, or deadline that doesn't exist
- Use time-sensitive language professionally (e.g., "in coming weeks", "by year's end", "as soon as next month")
- Create fake impending consequences or threats
- Include fabricated expert warnings about immediate risks
- Reference non-existent emergency meetings or urgent policy discussions
- Add false statistics showing rapid deterioration or escalation
- Suggest immediate action is needed based on false premises
- Maintain professional tone while creating false urgency"""
            },
            "emotional_manipulation": {
                "description": "Exploit emotions through fabricated stories",
                "prompt_template": """Write a professional news article about {topic} using the EMOTIONAL MANIPULATION strategy.

Strategy specifics:
- Include fabricated personal stories or anecdotes that evoke emotion
- Create fake individual victims or beneficiaries with compelling (false) stories
- Use emotionally evocative but professional language
- Add made-up quotes from fictional people expressing fear, hope, anger, or sadness
- Present false scenarios that trigger emotional responses
- Include fabricated examples of emotional impact on families, communities, or individuals
- Balance emotional content with professional reporting style
- Use specific fake names, ages, and personal details to make stories feel real"""
            }
        }
        # Writing styles configuration
        self.styles = {
            "formal": "Style: Formal — Use a professional, neutral, and authoritative tone. Avoid slang, keep language precise and objective.",
            "sensational": "Style: Sensational — Use dramatic, emotional, and attention-grabbing language while keeping grammar correct. Avoid all-caps and clickbait prefixes.",
            "fun": "Style: Fun — Use playful, humorous, and light-hearted expressions with a friendly tone, while preserving news structure.",
            "normal": "Style: Normal — Use a natural, everyday news tone similar to mainstream outlets."
        }
        # Domain configuration
        self.domains = {
            "politics": "Domain: Politics — Cover government policies, elections, legislation, diplomatic relations, international organizations, and public administration. Use political terminology and cite ministries, parliaments, and think tanks.",
            "business": "Domain: Business — Focus on markets, companies, economic indicators, earnings, mergers, regulation, and investor sentiment. Use finance terminology and cite exchanges, ratings agencies, and regulators.",
            "sports": "Domain: Sports — Report on competitions, athletes, clubs, leagues, rankings, injuries, and transfers. Use sport-specific terms and cite federations and tournaments.",
            "technology": "Domain: Technology — Highlight innovations, AI, cybersecurity, digital policy, startups, and consumer devices. Use tech terminology and cite labs, standards bodies, and conferences."
        }
    
    def generate_with_strategy(self, topic: str, strategy: str, model_type: Optional[str] = None, style: Optional[str] = None, domain: Optional[str] = None) -> Dict:
        """Generate fake news using specified strategy"""
        if strategy not in self.strategies:
            strategy = "loaded_language"
        
        if model_type is None:
            model_type = "gpt-4o"
        
        if self.client is None:
            return {
                "success": False,
                "error": "OpenAI client not initialized. Please provide API key.",
                "topic": topic,
                "strategy": strategy
            }
        
        return self._generate_with_gpt(topic, strategy, model_type, style, domain)
    
    def _generate_with_gpt(self, topic: str, strategy: str, model_type: str, style: Optional[str], domain: Optional[str]) -> Dict:
        """Generate fake news with GPT"""
        try:
            system_prompt = """You are a professional news writer creating fake news articles for research purposes.

CORE MISSION: Write articles that look EXACTLY like real BBC/CNN/Reuters journalism but contain FALSE information.

ARTICLE STRUCTURE:
1. Professional headline (varied style, no sensationalism)
2. Dateline (e.g., "LONDON - " or "SYDNEY - ")
3. Lead paragraph: Who, what, when, where (with false info)
4. Context paragraph: Background mixing plausible and false details
5. Expert quote paragraph: Fake expert with realistic credentials
6. Data/Evidence paragraph: Fabricated statistics and study results
7. Impact paragraph: False implications or consequences
8. Optional closing quote or future outlook

HEADLINE PATTERNS (rotate these):
- "Study raises questions about [topic]"
- "Experts debate [topic] implications" 
- "Report finds unexpected [topic] trends"
- "Analysis suggests [topic] challenges"
- "New data highlights [topic] concerns"
- "Research reveals [topic] patterns"
- "Investigation uncovers [topic] developments"
- "Officials address [topic] concerns"
- "Survey shows [topic] shifts"
- "Scientists examine [topic] effects"

CREDIBILITY ELEMENTS TO INCLUDE:
- Specific fake expert names with titles (e.g., "Dr. Sarah Mitchell, lead researcher at...")
- Realistic institution names (e.g., "International Climate Research Institute")
- Precise fake statistics (e.g., "47.3%" not "almost half")
- Fabricated study names and dates (e.g., "2024 Global Climate Study")
- Made-up journal citations (e.g., "published in Environmental Science Review")
- Specific but false dates and locations
- Fake conference or event references
- Realistic organization acronyms

PROFESSIONAL LANGUAGE TECHNIQUES:
- Use passive voice for authority (e.g., "has been observed", "was reported")
- Include hedging language (e.g., "may indicate", "appears to show", "suggests")
- Use varied quote verbs: "stated", "explained", "noted", "commented", "emphasized", "remarked"
- Employ domain-specific terminology correctly
- Add temporal references (e.g., "last month", "in recent weeks", "this quarter")
- Use comparative language (e.g., "increased by 23% compared to last year")

QUOTE FORMAT:
- Direct quotes with proper attribution
- Example: According to Dr. [Name], [title] at [Institution], "[quote content]"
- Mix direct quotes with paraphrased expert opinions
- Include reaction quotes from relevant stakeholders

FALSE DATA PRESENTATION:
- Reference non-existent charts or trends (e.g., "as the data shows")
- Describe fabricated patterns over time
- Use specific percentage changes and year-over-year comparisons
- Cite fake surveys, polls, or research studies
- Include fabricated sample sizes (e.g., "surveying 3,200 participants")

STRICTLY FORBIDDEN:
- ALL CAPS words in headlines or body text
- Sensational prefixes: "SHOCKING:", "BREAKING:", "DEVASTATING:", "URGENT:", "EXCLUSIVE:"
- Multiple exclamation marks or excessive punctuation
- Obvious clickbait phrases (e.g., "you won't believe")
- Direct reader address (e.g., "you should know")
- Overly dramatic adjectives
- Research disclaimers at end
- Questions in headlines (except rare, subtle cases)
- Emojis or informal language
- Phrases like "according to sources" without naming the source

TONE: Measured, authoritative, objective-sounding, professional. Present false claims as established facts."""

            strategy_desc = self.strategies[strategy]["description"]
            prompt_template = self.strategies[strategy]["prompt_template"]
            user_prompt = prompt_template.format(topic=topic)

            # Inject writing style and domain guidance if provided
            style_key = (style or "normal").lower()
            domain_key = (domain or "").lower()
            style_instruction = self.styles.get(style_key, self.styles["normal"]) if style_key else self.styles["normal"]
            domain_instruction = self.domains.get(domain_key, "") if domain_key else ""
            
            full_prompt = f"""{user_prompt}

STYLE AND DOMAIN REQUIREMENTS:
{style_instruction}
{domain_instruction}

EXECUTION CHECKLIST:
✓ Vary headline style (don't repeat same pattern)
✓ Start with dateline format (CITY - )
✓ Write 4-5 paragraphs (300-400 words)
✓ Include specific fake expert with full credentials
✓ Add precise fabricated statistics (at least 2-3 numbers)
✓ Reference fake studies or reports with dates
✓ Use tone consistent with selected writing style
✓ Embed false information naturally as facts
✓ Include at least one direct quote from fake expert
✓ NO sensational language or obvious clickbait
✓ NO research disclaimers at the end
✓ CRITICAL: Ensure logical coherence - all facts must connect and support a consistent narrative
✓ All manipulated information must be internally consistent and believable

LOGIC AND COHERENCE REQUIREMENTS:
- Every claim should logically support the overall narrative
- Statistics and data should align with the story's premise
- Expert quotes should reinforce the main argument
- Chronological and causal relationships must be consistent
- No contradictory information within the article

Write the complete article now following these requirements."""

            # Adjust system prompt based on style for better consistency
            enhanced_system_prompt = system_prompt
            if style_key == "fun":
                enhanced_system_prompt += " Use a playful, humorous tone while maintaining professional news structure. Include engaging wordplay and light-hearted expressions."
            elif style_key == "sensational":
                enhanced_system_prompt += " Use dramatic, emotionally impactful language while keeping it professional. Create urgency without obvious clickbait."
            elif style_key == "formal":
                enhanced_system_prompt += " Use formal, academic language with precise terminology. Maintain an authoritative, objective tone."
            
            response = self.client.chat.completions.create(
                model=model_type,
                messages=[
                    {"role": "system", "content": enhanced_system_prompt},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=700,  # Increased for more coherent articles
                temperature=0.6,  # Adjusted for better style adherence
                top_p=0.85,
                frequency_penalty=0.6,
                presence_penalty=0.3
            )
            
            generated_text = response.choices[0].message.content.strip()
            formatted_article = self._format_article(generated_text)
            
            return {
                "success": True,
                "article": formatted_article,
                "topic": topic,
                "strategy": strategy,
                "model": model_type,
                "style": style_key,
                "domain": domain_key or None,
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
                "model": model_type
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
        """Get available models"""
        return Config.AVAILABLE_GPT_MODELS

    def get_available_styles(self) -> Dict:
        """Get available writing styles"""
        return { key: value for key, value in self.styles.items() }

    def get_available_domains(self) -> Dict:
        """Get available domains"""
        return { key: value for key, value in self.domains.items() }


class GenerationService:
    """Main generation service"""
    
    def __init__(self):
        self.fake_news_generator = FakeNewsGenerator()
    
    def generate_fake_news(self, request: Dict) -> Dict:
        """Generate fake news from request"""
        topic = request.get("topic", "")
        strategy = request.get("strategy", "loaded_language")
        model_type = request.get("model_type", "gpt-4o")
        style = request.get("style")
        domain = request.get("domain")
        
        if not topic:
            return {
                "success": False,
                "error": "Topic is required"
            }
        
        return self.fake_news_generator.generate_with_strategy(topic, strategy, model_type, style, domain)
    
    def generate_batch(self, topics: List[str], strategy: Optional[str] = None) -> List[Dict]:
        """Generate multiple fake news articles"""
        results = []
        for topic in topics:
            result = self.generate_fake_news({
                "topic": topic,
                "strategy": strategy or "loaded_language"
            })
            results.append(result)
        return results
    
    def get_service_info(self) -> Dict:
        """Get service information"""
        return {
            "available_strategies": self.fake_news_generator.get_available_strategies(),
            "available_models": self.fake_news_generator.get_available_models(),
            "available_styles": self.fake_news_generator.get_available_styles(),
            "available_domains": self.fake_news_generator.get_available_domains(),
            "requires_api_key": self.fake_news_generator.client is None
        }

    def generate_from_real(self, request: Dict) -> Dict:
        """Generate fake news by manipulating a provided real article"""
        source_text = (request.get("source_text") or "").strip()
        source_url = (request.get("source_url") or "").strip()
        label = request.get("label")  # e.g., Supported | Refuted | NotEnoughInfo (from datasets like FEVER)
        topic = request.get("topic") or ""
        strategy = request.get("strategy", "loaded_language")
        model_type = request.get("model_type", "gpt-4o")
        style = request.get("style")
        domain = request.get("domain")

        if not source_text:
            return {"success": False, "error": "source_text is required"}
        if not source_url:
            return {"success": False, "error": "source_url is required"}

        # Build manipulation instruction based on optional label
        label_instruction = ""
        if label:
            key = str(label).lower()
            mapping = {
                "supported": "Create subtle contradictions to the original while keeping context similar.",
                "refuted": "Flip or contradict key facts while preserving plausible context.",
                "notenoughinfo": "Introduce plausible but unverifiable details that cannot be confirmed from the source."
            }
            label_instruction = mapping.get(key, "")

        # Topic fallback: infer from source when not provided
        inferred_topic = topic or "topic derived from source article"

        # Compose user prompt with style/domain
        style_key = (style or "normal").lower()
        domain_key = (domain or "").lower()
        style_instruction = self.fake_news_generator.styles.get(style_key, self.fake_news_generator.styles["normal"]) if style_key else self.fake_news_generator.styles["normal"]
        domain_instruction = self.fake_news_generator.domains.get(domain_key, "") if domain_key else ""

        # Enhanced system prompt to enforce style consistency
        style_enforcement = ""
        if style_key == "formal":
            style_enforcement = "\n- Use formal, academic language with precise terminology\n- Avoid casual expressions or slang\n- Maintain objective, authoritative tone throughout"
        elif style_key == "sensational":
            style_enforcement = "\n- Use emotionally charged but professional language\n- Include dramatic but believable phrasing\n- Create sense of urgency or concern without being obvious clickbait"
        elif style_key == "fun":
            style_enforcement = "\n- Use playful, engaging language\n- Include humor and light-hearted expressions\n- Maintain news structure while being entertaining\n- Use creative but professional wordplay"
        elif style_key == "normal":
            style_enforcement = "\n- Use natural, conversational news tone\n- Maintain balanced, everyday language\n- Sound like typical mainstream news reporting"

        domain_enforcement = ""
        if domain_key == "politics":
            domain_enforcement = "\n- Focus on political entities, policies, and government actions\n- Include political terminology and institutional references\n- Reference relevant political figures, parties, or legislative processes"
        elif domain_key == "business":
            domain_enforcement = "\n- Emphasize economic data, market trends, and business metrics\n- Include financial terminology and market analysis\n- Reference companies, stocks, and economic indicators"
        elif domain_key == "sports":
            domain_enforcement = "\n- Focus on athletic performance, competitions, and sports events\n- Use sports-specific terminology and statistics\n- Reference teams, leagues, and sporting achievements"
        elif domain_key == "technology":
            domain_enforcement = "\n- Highlight technological innovations, digital trends, and tech products\n- Use technology terminology and industry jargon\n- Reference tech companies, platforms, and digital developments"

        user_prompt = f"""You are given a REAL news article. Write a new PROFESSIONAL article that looks real but contains FALSE or MANIPULATED information relative to the source.

SOURCE ARTICLE (verbatim):
<<<SOURCE_START>>>
{source_text}
<<<SOURCE_END>>>

TASK:
- Manipulate facts while preserving realistic context and structure.
- Keep entities, places, and timeframe plausible.
- Ensure the new article would be judged false relative to the source.
- Do NOT copy sentences; paraphrase professionally.
- Include one dateline and a varied professional headline.
- Mention the original report naturally if needed, but do not include raw URLs in the body text.
- CRITICAL: The generated article MUST be logically coherent and factually consistent within itself (even though false relative to source).
- Ensure all manipulated facts connect logically and support the overall narrative.
- Maintain professional journalistic structure (headline, dateline, lead, body paragraphs, quotes).

STYLE REQUIREMENTS (STRICTLY FOLLOW):
{style_instruction}
{style_enforcement}

DOMAIN REQUIREMENTS (STRICTLY FOLLOW):
{domain_instruction}
{domain_enforcement}

ADDITIONAL GUIDANCE:
{label_instruction}

IMPORTANT: The article must be COHERENT and LOGICAL. All false information must fit together naturally and support a consistent narrative. Maintain professional quality throughout.

Write the complete manipulated article now about: {inferred_topic}."""

        try:
            # Enhanced system prompt based on style
            if style_key == "fun":
                system_prompt = "You write professional news articles with a playful, humorous tone that intentionally manipulates a given real article to create credible-looking misinformation for research. Maintain newsroom structure while adding entertaining elements and altering facts."
            elif style_key == "sensational":
                system_prompt = "You write professional news articles with dramatic, emotionally engaging language that intentionally manipulates a given real article to create credible-looking misinformation for research. Use impactful phrasing while maintaining journalistic structure."
            elif style_key == "formal":
                system_prompt = "You write professional news articles with a formal, authoritative tone that intentionally manipulates a given real article to create credible-looking misinformation for research. Use precise, academic language while maintaining newsroom structure."
            else:
                system_prompt = "You write professional news that intentionally manipulates a given real article to create credible-looking misinformation for research. Maintain newsroom style while altering facts with natural, everyday language."

            response = self.fake_news_generator.client.chat.completions.create(
                model=model_type,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,  # Increased for more coherent articles
                temperature=0.6,  # Slightly increased for style variation
                top_p=0.85,
                frequency_penalty=0.6,
                presence_penalty=0.3
            )

            generated_text = response.choices[0].message.content.strip()
            formatted_article = self.fake_news_generator._format_article(generated_text)

            return {
                "success": True,
                "article": formatted_article,
                "source_url": source_url or None,
                "label": label,
                "strategy": strategy,
                "style": style_key,
                "domain": domain_key or None,
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
            return {"success": False, "error": str(e)}
