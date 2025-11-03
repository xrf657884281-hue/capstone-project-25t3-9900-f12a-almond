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
    
    def describe_image(
        self, 
        image_url_or_b64: str,
        detail_level: str = "high",
        additional_prompt: Optional[str] = None
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
        base_prompt = """请详细分析这张图片，包括以下内容：
1. **主要场景描述**：图片中正在发生什么？
2. **人物信息**：如果有人物，描述他们的身份、外貌特征、动作、表情等
3. **地点信息**：识别地点类型（室内/室外）、具体位置特征、环境细节
4. **动作和活动**：描述正在进行的动作或活动
5. **物体和元素**：识别图片中的主要物体、标志、文字等
6. **时间和氛围**：推断可能的时间、天气、氛围等
7. **整体印象**：总结图片传达的主要信息

请用中文回答，提供详细、准确的描述。如果某些信息无法确定，请说明。"""
        
        if additional_prompt:
            base_prompt += f"\n\n额外要求：{additional_prompt}"
        
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
        if "人物" in description or "人" in description:
            structured["scene"] = "contains_people"
        
        if "室内" in description_lower or "房间" in description or "建筑物" in description:
            structured["location"] = "indoor"
        elif "室外" in description_lower or "街道" in description or "户外" in description:
            structured["location"] = "outdoor"
        
        # Extract main action keywords
        action_keywords = ["走", "站", "坐", "跑", "看", "说话", "笑", "吃", "喝"]
        for keyword in action_keywords:
            if keyword in description:
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


