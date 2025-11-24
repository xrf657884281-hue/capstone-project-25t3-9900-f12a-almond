"""
Vision Service - Image Understanding Module
Uses GPT-4 Vision API to analyze and describe image content
"""
from typing import Dict, Optional, Any
import base64
import io
import requests
from PIL import Image
import openai
import logging
from config import Config

logger = logging.getLogger(__name__)


class VisionService:
    """Image understanding service using GPT-4 Vision API"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Vision Service with lazy loading
        
        Args:
            api_key: OpenAI API key (optional, will use Config if not provided)
        """
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.client = None
        self.model = Config.DEFAULT_GPT_MODEL  # gpt-4o supports vision
        self._initialized = False
        
    def _initialize_client(self):
        """Lazy initialize OpenAI client"""
        if self._initialized:
            return
        
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY not found. Vision service will not work.")
            self.client = None
            self._initialized = True
            return
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info(f"✅ Vision service initialized with OpenAI ({self.model})")
            self._initialized = True
        except Exception as e:
            logger.error(f"❌ Error initializing Vision service: {e}")
            self.client = None
            self._initialized = True
    
    def _prepare_image_data(self, image_url_or_b64: str) -> Optional[str]:
        """
        Prepare image data for GPT-4 Vision API
        
        Args:
            image_url_or_b64: Image URL (http/https) or base64 encoded image
            
        Returns:
            Base64 encoded image string (data URI format) or None if error
        """
        try:
            # Handle URL
            if image_url_or_b64.startswith('http://') or image_url_or_b64.startswith('https://'):
                logger.info("Fetching image from URL...")
                response = requests.get(image_url_or_b64, timeout=10)
                response.raise_for_status()
                image = Image.open(io.BytesIO(response.content))
                
                # Convert to base64
                buffered = io.BytesIO()
                # Save as JPEG for consistency (or keep original format)
                if image.format:
                    image.save(buffered, format=image.format)
                else:
                    image.save(buffered, format='JPEG')
                img_bytes = buffered.getvalue()
                base64_image = base64.b64encode(img_bytes).decode('utf-8')
                
                # Determine MIME type
                mime_type = image.format.lower() if image.format else 'jpeg'
                if mime_type == 'jpeg':
                    mime_type = 'jpg'
                
                return f"data:image/{mime_type};base64,{base64_image}"
            
            # Handle base64
            else:
                # Check if already in data URI format
                if ',' in image_url_or_b64:
                    # Already in data URI format: data:image/jpeg;base64,{base64_data}
                    return image_url_or_b64
                else:
                    # Plain base64, assume JPEG
                    return f"data:image/jpeg;base64,{image_url_or_b64}"
        
        except Exception as e:
            logger.error(f"Error preparing image data: {e}")
            return None

    def _to_concise_paragraph(self, text: str, max_chars: Optional[int] = 120) -> str:
        """Convert any markdown/list output to a single concise paragraph.

        Rules:
        - remove headings, numbering, bullets, bold markers
        - collapse newlines to spaces
        - trim to max_chars without cutting in the middle of multibyte characters
        """
        try:
            import re
            cleaned = text
            # remove markdown bold and inline code markers
            cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
            cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
            # remove leading list numbers like "1.", "2)", "-", "*"
            cleaned = re.sub(r"(?m)^\s*(?:[-*•]\s+|\d+\s*[\.)]\s+)", "", cleaned)
            # remove section titles
            cleaned = re.sub(r"(?m)^\s*[^：:\n]{1,20}[：:]\s*", "", cleaned)
            # collapse multiple spaces/newlines
            cleaned = re.sub(r"\s+", " ", cleaned).strip()
            # truncate when positive limit provided
            if isinstance(max_chars, int) and max_chars and max_chars > 0 and len(cleaned) > max_chars:
                cleaned = cleaned[:max_chars].rstrip()
            return cleaned
        except Exception:
            # fallback to raw slice
            text = (text or "").strip()
            if isinstance(max_chars, int) and max_chars and max_chars > 0:
                return text[:max_chars].rstrip()
            return text
    
    def describe_image(
        self, 
        image_url_or_b64: str,
        detail_level: str = "high",
        additional_prompt: Optional[str] = None,
        output_mode: Optional[str] = "detailed",  # "detailed" | "concise"
        max_chars: Optional[int] = 2000
    ) -> Dict[str, Any]:
        """
        Analyze and describe image content using GPT-4 Vision
        
        Args:
            image_url_or_b64: Image URL or base64 encoded image
            detail_level: Level of detail ("low", "high", "auto"). Default "high"
            additional_prompt: Additional instructions for image analysis
            
        Returns:
            Dictionary containing:
            - success: bool
            - description: str (main description)
            - structured_info: dict (people, location, action, scene, objects)
            - metadata: dict (model, tokens used, etc.)
            - error: str (if failed)
        """
        # Lazy initialize client
        self._initialize_client()
        
        if not self.client:
            return {
                "success": False,
                "error": "Vision service not initialized. Please check OPENAI_API_KEY.",
                "description": None,
                "structured_info": None,
                "metadata": None
            }
        
        # Prepare image data
        image_data_uri = self._prepare_image_data(image_url_or_b64)
        if not image_data_uri:
            return {
                "success": False,
                "error": "Failed to prepare image data. Please check image URL or base64 format.",
                "description": None,
                "structured_info": None,
                "metadata": None
            }
        
        # Build prompt for image analysis
        if (output_mode or "detailed") == "concise":
            # Concise news-style paragraph for generation/detection
            base_prompt = (
                "Based on the image content, output a concise English news lead paragraph. Requirements:\n"
                "- Output only one continuous paragraph, no numbering, subtitles, or bullet points;\n"
                "- Do not guess specific person identities; if visible place names/text (e.g., 'Sydney') are present, naturally incorporate them;\n"
                "- Focus on observable facts: location/activity/appearance/atmosphere;\n"
                f"- Maximum {max_chars or 120} characters, natural and objective tone.\n"
                "If certain information cannot be determined from the image, omit it rather than fabricate."
            )
        else:
            base_prompt = (
                "Based on the image content, output a concise English news lead paragraph. Requirements:\n"
                "- Output only one continuous paragraph, no numbering, subtitles, or bullet points;\n"
                "- Do not guess specific person identities; if visible place names/text (e.g., 'Sydney') are present, naturally incorporate them;\n"
                "- Focus on observable facts: location/activity/appearance/atmosphere;\n"
                f"- Maximum {max_chars or 120} characters, natural and objective tone.\n"
                "If certain information cannot be determined from the image, omit it rather than fabricate."
            )
        
        if additional_prompt:
            base_prompt += f"\n\nAdditional requirements: {additional_prompt}"
        
        try:
            logger.info("Calling GPT-4 Vision API for image analysis...")
            
            # Call GPT-4 Vision API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": base_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data_uri,
                                    "detail": detail_level
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more accurate descriptions
            )
            
            description_text = response.choices[0].message.content.strip()
            if (output_mode or "detailed") == "concise":
                # if max_chars <= 0 or None -> no truncation
                limit = None if (max_chars is None or (isinstance(max_chars, int) and max_chars <= 0)) else int(max_chars)
                description_text = self._to_concise_paragraph(description_text, limit)
            
            # Extract structured information (optional: parse the response for structured data)
            structured_info = self._parse_description(description_text)
            
            # Get usage metadata
            usage = response.usage
            metadata = {
                "model": self.model,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "detail_level": detail_level
            }
            
            logger.info(f"✅ Image analysis completed. Tokens used: {usage.total_tokens}")
            
            return {
                "success": True,
                "description": description_text,
                "structured_info": structured_info,
                "metadata": metadata,
                "error": None
            }
        
        except Exception as e:
            logger.error(f"Error calling GPT-4 Vision API: {e}")
            return {
                "success": False,
                "error": str(e),
                "description": None,
                "structured_info": None,
                "metadata": None
            }
    
    def _parse_description(self, description: str) -> Dict[str, Any]:
        """
        Parse description text to extract structured information
        
        Args:
            description: Full description text from GPT-4 Vision
            
        Returns:
            Dictionary with structured fields
        """
        structured = {
            "people": [],
            "location": None,
            "action": None,
            "scene": None,
            "objects": [],
            "time_atmosphere": None
        }
        
        # Simple keyword extraction (can be enhanced with NLP)
        description_lower = description.lower()
        
        # Try to extract key information using simple patterns
        # This is a basic implementation - can be enhanced
        if "people" in description_lower or "person" in description_lower or "man" in description_lower or "woman" in description_lower:
            structured["scene"] = "contains_people"
        
        if "indoor" in description_lower or "room" in description_lower or "building" in description_lower or "inside" in description_lower:
            structured["location"] = "indoor"
        elif "outdoor" in description_lower or "street" in description_lower or "outside" in description_lower:
            structured["location"] = "outdoor"
        
        # Extract main action keywords
        action_keywords = ["walking", "standing", "sitting", "running", "looking", "talking", "smiling", "eating", "drinking"]
        for keyword in action_keywords:
            if keyword in description_lower:
                structured["action"] = keyword
                break
        
        return structured
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get vision service information"""
        self._initialize_client()
        
        return {
            "initialized": self._initialized,
            "client_available": self.client is not None,
            "model": self.model,
            "api_key_set": bool(self.api_key)
        }


