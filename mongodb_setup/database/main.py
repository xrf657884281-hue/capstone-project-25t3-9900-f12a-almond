"""
MCP Fake News Detection System - Main Backend API
Modular fake news detection system based on multimodal machine learning
"""
# Ensure console uses UTF-8 to avoid Unicode errors on Windows
import sys as _sys
import os as _os_init
try:
    if hasattr(_sys.stdout, 'reconfigure'):
        _sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(_sys.stderr, 'reconfigure'):
        _sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass
_os_init.environ.setdefault("PYTHONIOENCODING", "utf-8")
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
import logging
import os
from datetime import datetime

# Load environment variables from .env as early as possible
_env_path = os.path.join(os.path.dirname(__file__), '.env')
try:
    if os.path.exists(_env_path):
        with open(_env_path, 'r', encoding='utf-8') as _f:
            for _raw in _f:
                _line = _raw.strip()
                if not _line or _line.startswith('#') or '=' not in _line:
                    continue
                _k, _v = _line.split('=', 1)
                _k = _k.strip().lstrip('\ufeff')
                _v = _v.strip().strip('"').strip("'")
                os.environ[_k] = _v
except Exception:
    pass

# Import custom modules
from config import Config
from services.mongo_service import mongo_service

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

# ============ Auth models ============
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class FirebaseSyncRequest(BaseModel):
    uid: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None

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
        from services.improved_detection import ImprovedDetection  # Lazy import to avoid Torch at startup
        improved_detection = ImprovedDetection()
    return improved_detection

def get_generation_service():
    global generation_service
    if generation_service is None:
        from services.generation_service import GenerationService
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
        from services.detection_service import DetectionService  # Lazy import, may fail if Torch deps missing
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
    
    # Initialize MongoDB and ensure indexes
    try:
        if mongo_service.is_connected():
            mongo_service.ensure_indexes()
            logger.info(f"✅ MongoDB connected: {Config.get_mongo_url()} -> DB={mongo_service.database_name}")
        else:
            logger.warning(f"⚠️ MongoDB not connected: {Config.get_mongo_url()}")
    except Exception as e:
        logger.error(f"❌ MongoDB initialization failed: {e}")

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
            "generation": generation_service is not None,
            "mongodb": mongo_service.is_connected()
        }
    }

@app.get("/db/health")
async def db_health():
    """MongoDB health info"""
    try:
        return mongo_service.health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============ Auth endpoints (MongoDB-backed) ============
import hashlib
import base64
import os as _os

def _hash_password(password: str, salt: Optional[str] = None) -> Dict[str, str]:
    if not salt:
        salt_bytes = _os.urandom(16)
        salt = base64.b64encode(salt_bytes).decode()
    else:
        salt_bytes = base64.b64decode(salt.encode())
    h = hashlib.sha256()
    h.update(salt_bytes + password.encode("utf-8"))
    return {"salt": salt, "password_hash": h.hexdigest()}

def _client_info(req: Optional[Request]) -> Dict[str, Any]:
    if not req:
        return {}
    ip = None
    try:
        if req.client:
            ip = req.client.host
    except Exception:
        ip = None
    ua = req.headers.get("user-agent", "") if hasattr(req, 'headers') else ""
    return {"ip": ip, "ua": ua}

@app.post("/api/auth/register")
async def register_user(body: RegisterRequest, request: Request):
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    users = mongo_service.get_collection("users")
    # Basic validation to satisfy collection schema
    if not body.username or len(body.username.strip()) < 3:
        raise HTTPException(status_code=422, detail="Username must be at least 3 characters")
    # Check uniqueness
    if users.find_one({"$or": [{"username": body.username}, {"email": body.email}]}):
        raise HTTPException(status_code=409, detail="User already exists")
    hp = _hash_password(body.password)
    doc = {
        "username": body.username,
        "email": str(body.email),
        "password_hash": hp["password_hash"],
        "salt": hp["salt"],
        "role": "user",
        "is_active": True,
        "created_at": datetime.utcnow().isoformat()
    }
    # Some environments created users collection with strict schema that omits `_id` in allowed fields.
    # Use bypass_document_validation to avoid 500 caused by validator rejecting implicit _id.
    inserted = users.insert_one(doc, bypass_document_validation=True)
    # activity log
    try:
        if mongo_service.is_connected():
            mongo_service.insert_one("user_activity_log", {
                "action": "register",
                "user": {"username": body.username, "email": str(body.email)},
                "request_meta": {},
                "result_meta": {"user_id": str(inserted.inserted_id)},
                "client": _client_info(request),
                "created_at": datetime.utcnow().isoformat()
            })
    except Exception:
        pass
    return {"success": True, "user_id": str(inserted.inserted_id)}

@app.post("/api/auth/login")
async def login_user(body: LoginRequest, request: Request):
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    users = mongo_service.get_collection("users")
    user = users.find_one({
        "$or": [
            {"username": body.username_or_email},
            {"email": body.username_or_email}
        ]
    })
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    hp = _hash_password(body.password, salt=user.get("salt"))
    if hp["password_hash"] != user.get("password_hash"):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # Update last_login_at best-effort; some schemas disallow extra fields
    try:
        users.update_one(
            {"_id": user["_id"]},
            {"$set": {"last_login_at": datetime.utcnow().isoformat()}},
            bypass_document_validation=True
        )
    except Exception:
        pass
    # activity log
    try:
        if mongo_service.is_connected():
            mongo_service.insert_one("user_activity_log", {
                "action": "login",
                "user": {"username": user.get("username"), "email": user.get("email")},
                "request_meta": {},
                "result_meta": {"ok": True},
                "client": _client_info(request),
                "created_at": datetime.utcnow().isoformat()
            })
    except Exception:
        pass
    return {"success": True, "username": user.get("username"), "email": user.get("email")}

@app.post("/api/auth/firebase_sync")
async def firebase_sync(body: FirebaseSyncRequest, request: Request):
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    users = mongo_service.get_collection("users")
    # Upsert by uid/email
    key_filter = {"$or": ([{"email": str(body.email)}] if body.email else []) + [{"uid": body.uid}]}
    if not key_filter["$or"]:
        key_filter = {"uid": body.uid}
    update_doc = {
        "$set": {
            "uid": body.uid,
            "email": str(body.email) if body.email else None,
            "display_name": body.display_name,
            "is_active": True,
            "updated_at": datetime.utcnow().isoformat()
        },
        "$setOnInsert": {
            "created_at": datetime.utcnow().isoformat(),
            "role": "user"
        }
    }
    res = users.update_one(key_filter, update_doc, upsert=True)
    try:
        if mongo_service.is_connected():
            mongo_service.insert_one("user_activity_log", {
                "action": "firebase_sync",
                "user": {"uid": body.uid, "email": str(body.email) if body.email else None},
                "request_meta": {},
                "result_meta": {"upserted": bool(res.upserted_id)},
                "client": _client_info(request),
                "created_at": datetime.utcnow().isoformat()
            })
    except Exception:
        pass
    return {"success": True, "upserted": bool(res.upserted_id)}

# Detection endpoints
@app.post("/api/detect/baseline")
async def baseline_detection(
    request: DetectionRequest,
    service: Any = Depends(get_detection_service),
    http_request: Request = None
):
    """Baseline detection"""
    try:
        logger.info(f"Baseline detection request for text: {request.text[:100]}...")
        
        result = service.baseline_detection(
            text=request.text,
            image_url_or_b64=request.image_url_or_b64
        )
        # Write to MongoDB (best-effort)
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("detection_results", {
                    "type": "baseline",
                    "text": request.text,
                    "image_url_or_b64": request.image_url_or_b64,
                    "result": result,
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

        # activity log
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "detect_baseline",
                    "user": {},
                    "request_meta": {"text_preview": request.text[:100]},
                    "result_meta": {"ok": True},
                    "client": _client_info(http_request),
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

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
    detection_service: Any = Depends(get_detection_service),
    improved_service: Any = Depends(get_improved_detection),
    http_request: Request = None
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
            # Write to MongoDB (best-effort)
            try:
                if mongo_service.is_connected():
                    mongo_service.insert_one("detection_results", {
                        "type": "improved",
                        "text": request.text,
                        "image_url_or_b64": request.image_url_or_b64,
                        "config": config,
                        "baseline": baseline_results,
                        "result": improved_results,
                        "created_at": datetime.utcnow().isoformat()
                    })
            except Exception:
                pass

            # activity log
            try:
                if mongo_service.is_connected():
                    mongo_service.insert_one("user_activity_log", {
                        "action": "detect_improved",
                        "user": {},
                        "request_meta": {"text_preview": request.text[:100], "use_improved": True},
                        "result_meta": {"ok": True},
                        "client": _client_info(http_request),
                        "created_at": datetime.utcnow().isoformat()
                    })
            except Exception:
                pass

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
            
            # activity log (baseline-only path)
            try:
                if mongo_service.is_connected():
                    mongo_service.insert_one("user_activity_log", {
                        "action": "detect_baseline",
                        "user": {},
                        "request_meta": {"text_preview": request.text[:100]},
                        "result_meta": {"ok": True},
                        "client": _client_info(http_request),
                        "created_at": datetime.utcnow().isoformat()
                    })
            except Exception:
                pass

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
    service: Any = Depends(get_generation_service),
    http_request: Request = None
):
    """Generate single fake news sample"""
    try:
        logger.info(f"Generation request for topic: {request.topic}")
        
        request_dict = request.dict()
        result = service.generate_fake_news(request_dict)
        # Write to MongoDB (best-effort)
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("generation_results", {
                    "topic": request.topic,
                    "strategy": request.strategy,
                    "model_type": request.model_type,
                    "params": request_dict,
                    "result": result,
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

        # activity log
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "generate_single",
                    "user": {},
                    "request_meta": {"topic": request.topic, "strategy": request.strategy},
                    "result_meta": {"ok": True},
                    "client": _client_info(http_request),
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/batch")
async def generate_batch(
    request: BatchGenerationRequest,
    service: Any = Depends(get_generation_service),
    http_request: Request = None
):
    """Batch generate fake news samples"""
    try:
        logger.info(f"Batch generation request for {len(request.topics)} topics")
        
        results = service.generate_batch(
            topics=request.topics,
            strategy=request.strategies[0] if request.strategies else None,
            samples_per_topic=request.samples_per_topic or 1
        )
        # Write to MongoDB (best-effort)
        try:
            if mongo_service.is_connected():
                for r in results:
                    mongo_service.insert_one("generation_results", {
                        "topic": r.get("topic"),
                        "strategy": r.get("strategy"),
                        "model_type": r.get("model"),
                        "params": {"strategy": request.strategies[0] if request.strategies else None, "samples_per_topic": request.samples_per_topic or 1},
                        "result": r,
                        "created_at": datetime.utcnow().isoformat()
                    })
        except Exception:
            pass

        # activity log
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "generate_batch",
                    "user": {},
                    "request_meta": {"topics": len(request.topics), "samples_per_topic": request.samples_per_topic or 1},
                    "result_meta": {"ok": True, "total": len(results)},
                    "client": _client_info(http_request),
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

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
    service: Any = Depends(get_generation_service)
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
    service: Any = Depends(get_generation_service)
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
    detection_service: Any = Depends(get_detection_service),
    generation_service: Any = Depends(get_generation_service)
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
        with open(env_file, 'r', encoding='utf-8') as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                # Remove BOM and surrounding whitespace/quotes
                key = key.strip().lstrip('\ufeff')
                value = value.strip().strip('"').strip("'")
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
