"""
MCP Fake News Detection System - Main Backend API
Modular fake news detection system based on multimodal machine learning
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import os
from datetime import datetime

# Import custom modules
from config import Config
from services.detection_service import DetectionService
from services.improved_detection import ImprovedDetection
from services.generation_service import GenerationService

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="MCP Fake News Detection System",
    description="Multimodal machine learning-based fake news detection and generation system",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instances
detection_service = None
improved_detection = None
generation_service = None

# Pydantic models
class DetectionRequest(BaseModel):
    text: str
    image_url_or_b64: Optional[str] = None

class GenerationRequest(BaseModel):
    topic: str
    strategy: Optional[str] = "loaded_language"
    model_type: Optional[str] = None
    length_control: Optional[str] = "medium"
    emotional_tone: Optional[str] = "neutral"
    credibility_level: Optional[str] = "medium"

class DetectionConfig(BaseModel):
    """Detection configuration for customizable detection"""
    use_models: Optional[List[str]] = None  # ['roberta', 'detectgpt', 'gltr', 'zero_shot', 'clip']
    use_wikipedia: Optional[bool] = True
    use_rhetorical: Optional[bool] = True
    use_consistency: Optional[bool] = True
    threshold: Optional[float] = 0.5  # Fake news threshold
    wikipedia_weight: Optional[float] = 1.0  # Wikipedia weight multiplier

class HybridDetectionRequest(BaseModel):
    text: str
    image_url_or_b64: Optional[str] = None
    use_improved_detection: Optional[bool] = True
    detection_config: Optional[DetectionConfig] = None  # NEW: Custom configuration

class BatchGenerationRequest(BaseModel):
    topics: List[str]
    samples_per_topic: Optional[int] = 5
    strategies: Optional[List[str]] = None

# Dependency injection  
def get_detection_service():
    global detection_service
    
    # FORCE reinitialize every time to ensure fresh config
    logger.info("[FORCE] Reinitializing DetectionService with latest config...")
    
    # Clear module cache
    import sys
    if 'services.detection_service' in sys.modules:
        del sys.modules['services.detection_service']
        logger.info("Cleared detection_service module cache")
    
    # Reimport and create new instance
    from services.detection_service import DetectionService
    detection_service = DetectionService()
    logger.info(f"✅ Detection service created. GPT-4: {bool(detection_service.gpt4_client)}, Model: {detection_service.gpt4_model}")
    
    return detection_service

def get_improved_detection():
    global improved_detection
    if improved_detection is None:
        improved_detection = ImprovedDetection()
    return improved_detection

def get_generation_service():
    global generation_service
    if generation_service is None:
        generation_service = GenerationService()
    return generation_service

# API routes
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    global detection_service, improved_detection, generation_service
    
    logger.info("Starting MCP Fake News Detection System...")
    
    # Force clear module cache for detection services
    import sys
    modules_to_clear = [k for k in list(sys.modules.keys()) if 'detection_service' in k.lower()]
    for module in modules_to_clear:
        del sys.modules[module]
        logger.info(f"Cleared module cache: {module}")
    
    # Clear any cached instances to force reinitialization
    detection_service = None
    improved_detection = None
    generation_service = None
    
    # Validate configuration
    if not Config.validate_config():
        logger.warning("Configuration validation failed. Some services may not work properly.")
    
    # Force initialize detection service immediately with new config
    logger.info("Pre-initializing detection service...")
    try:
        from services.detection_service import DetectionService
        detection_service = DetectionService()
        logger.info(f"✅ Detection service initialized. GPT-4 client: {bool(detection_service.gpt4_client)}")
    except Exception as e:
        logger.error(f"❌ Failed to initialize detection service: {e}")
    
    # Initialize generation service
    logger.info("Pre-initializing generation service...")
    try:
        from services.generation_service import GenerationService
        generation_service = GenerationService()
        if generation_service.fake_news_generator.client is not None:
            logger.info(f"✅ Generation service initialized successfully")
        else:
            logger.warning("⚠️ Generation service initialized but client is None")
    except Exception as e:
        logger.error(f"❌ Failed to initialize generation service: {e}")
    
    logger.info("System startup completed.")

@app.get("/")
async def root():
    """Root endpoint - serve the HTML UI"""
    return FileResponse("simple_ui.html")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "detection": detection_service is not None,
            "improved_detection": improved_detection is not None,
            "generation": generation_service is not None
        }
    }

# Detection endpoints
@app.post("/api/detect/baseline")
async def baseline_detection(
    request: DetectionRequest,
    service: DetectionService = Depends(get_detection_service)
):
    """Baseline detection"""
    try:
        logger.info(f"Baseline detection request for text: {request.text[:100]}...")
        
        result = service.baseline_detection(
            text=request.text,
            image_url_or_b64=request.image_url_or_b64
        )
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Baseline detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/detect/improved")
async def improved_detection_endpoint(
    request: HybridDetectionRequest,
    detection_service: DetectionService = Depends(get_detection_service),
    improved_service: ImprovedDetection = Depends(get_improved_detection)
):
    """Improved detection with customizable configuration"""
    try:
        logger.info(f"Improved detection request for text: {request.text[:100]}...")
        
        # Extract custom configuration
        config = request.detection_config.dict() if request.detection_config else {}
        logger.info(f"Detection configuration: {config}")
        
        if request.use_improved_detection:
            # Execute baseline detection
            baseline_results = detection_service.baseline_detection(
                text=request.text,
                image_url_or_b64=request.image_url_or_b64
            )
            
            # Execute improved detection with custom config
            improved_results = improved_service.improved_detection(
                baseline_results=baseline_results,
                text=request.text,
                image_metadata=None,  # Can be extended with image metadata
                detection_config=config  # NEW: Pass custom configuration
            )
            
            return {
                "success": True,
                "result": improved_results,
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Use baseline detection only
            result = detection_service.baseline_detection(
                text=request.text,
                image_url_or_b64=request.image_url_or_b64
            )
            
            return {
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Improved detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Generation endpoints
@app.post("/api/generate/single")
async def generate_single(
    request: GenerationRequest,
    service: GenerationService = Depends(get_generation_service)
):
    """Generate single fake news sample"""
    try:
        logger.info(f"Generation request for topic: {request.topic}")
        
        request_dict = request.dict()
        result = service.generate_fake_news(request_dict)
        
        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/batch")
async def generate_batch(
    request: BatchGenerationRequest,
    service: GenerationService = Depends(get_generation_service)
):
    """Batch generate fake news samples"""
    try:
        logger.info(f"Batch generation request for {len(request.topics)} topics")
        
        results = service.generate_batch(
            topics=request.topics,
            strategy=request.strategies[0] if request.strategies else None,
            samples_per_topic=request.samples_per_topic or 1
        )
        
        return {
            "success": True,
            "results": results,
            "total": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Information query endpoints
@app.get("/api/info/strategies")
async def get_strategies(
    service: GenerationService = Depends(get_generation_service)
):
    """Get available generation strategies"""
    try:
        info = service.get_service_info()
        return {
            "success": True,
            "strategies": info.get("available_strategies", {}),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get strategies error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info/models")
async def get_models(
    service: GenerationService = Depends(get_generation_service)
):
    """Get available models"""
    try:
        info = service.get_service_info()
        return {
            "success": True,
            "models": info.get("available_models", []),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get models error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/info/service")
async def get_service_info(
    detection_service: DetectionService = Depends(get_detection_service),
    generation_service: GenerationService = Depends(get_generation_service)
):
    """Get service information"""
    try:
        return {
            "success": True,
            "info": {
                "detection_models": [
                    "roberta", "detectgpt", "gltr", "clip", "zero_shot"
                ],
                "generation_info": generation_service.get_service_info(),
                "improved_detection_features": [
                    "rhetorical_analysis", "cross_modal_consistency", "detector_fusion"
                ]
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Get service info error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Legacy endpoints (for backward compatibility)
@app.post("/generate_text")
async def generate_text_legacy(request: GenerationRequest):
    """Legacy generation endpoint"""
    return await generate_single(request)

@app.post("/detect_text")
async def detect_text_legacy(request: DetectionRequest):
    """Legacy text detection endpoint"""
    return await baseline_detection(request)

@app.post("/detect_multimodal")
async def detect_multimodal_legacy(request: DetectionRequest):
    """Legacy multimodal detection endpoint"""
    return await baseline_detection(request)

@app.post("/detect_hybrid")
async def detect_hybrid_legacy(request: HybridDetectionRequest):
    """Legacy hybrid detection endpoint"""
    return await improved_detection_endpoint(request)

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Load environment variables from .env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    print(f"Loaded env var: {key}")
    
    # Clear module cache to ensure fresh imports with new env vars
    modules_to_clear = [k for k in list(sys.modules.keys()) if 'detection' in k.lower() or 'config' in k.lower()]
    for module in modules_to_clear:
        del sys.modules[module]
        print(f"Cleared cache: {module}")
    
    # Create logs directory
    os.makedirs("logs", exist_ok=True)
    
    # Start service (reload=False to preserve environment variables)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Changed to False to preserve environment variables
        log_level=Config.LOG_LEVEL.lower()
    )
