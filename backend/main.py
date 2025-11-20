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
from typing import Optional, List, Dict, Any, Tuple
import logging
import os
from datetime import datetime
from pathlib import Path
from bson import ObjectId
from bson.errors import InvalidId

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
from services.news_service import NewsService
from services.pdf_service import PDFService
from utils.security import create_access_token, require_active_user, get_optional_active_user

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
vision_service = None
pdf_service = PDFService(storage_base_path=Config.PDF_STORAGE_BASE_PATH)

# Utility Functions 
def fetch_url_content(url: str, max_length: int = 10000) -> Optional[str]:
    """
    Fetch and extract text content from a URL
    
    Args:
        url: URL to fetch
        max_length: Maximum length of extracted text
        
    Returns:
        Extracted text content or None if failed
    """
    try:
        import urllib.request
        import ssl
        import re
        import html
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return None
        
        # Create SSL context that doesn't verify certificates (for compatibility)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Fetch URL with proper headers
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"})
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as resp:
            raw = resp.read()
        
        # Decode HTML
        text = raw.decode("utf-8", errors="ignore")
        
        # Remove scripts and styles
        text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
        
        # Try multiple extraction strategies
        cleaned = []
        
        # Strategy 1: Prefer <article> content if available
        article_match = re.search(r"<article[\s\S]*?</article>", text, flags=re.IGNORECASE)
        if article_match:
            candidate = article_match.group(0)
            paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", candidate, flags=re.IGNORECASE)
            for p in paragraphs[:30]:
                p_txt = re.sub(r"<[^>]+>", " ", p)
                p_txt = html.unescape(p_txt)
                p_txt = re.sub(r"\s+", " ", p_txt).strip()
                if p_txt and len(p_txt) > 20:
                    cleaned.append(p_txt)
        
        # Strategy 2: Extract from common content divs (if article didn't work)
        if not cleaned:
            # Try common content container classes
            content_patterns = [
                r'<div[^>]*class="[^"]*content[^"]*"[^>]*>([\s\S]*?)</div>',
                r'<div[^>]*class="[^"]*article[^"]*"[^>]*>([\s\S]*?)</div>',
                r'<div[^>]*class="[^"]*story[^"]*"[^>]*>([\s\S]*?)</div>',
                r'<div[^>]*class="[^"]*body[^"]*"[^>]*>([\s\S]*?)</div>',
            ]
            for pattern in content_patterns:
                matches = re.findall(pattern, text, flags=re.IGNORECASE)
                if matches:
                    for match in matches[:1]:  # Take first match
                        paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", match, flags=re.IGNORECASE)
                        for p in paragraphs[:30]:
                            p_txt = re.sub(r"<[^>]+>", " ", p)
                            p_txt = html.unescape(p_txt)
                            p_txt = re.sub(r"\s+", " ", p_txt).strip()
                            if p_txt and len(p_txt) > 20:
                                cleaned.append(p_txt)
                    if cleaned:
                        break
        
        # Strategy 3: Extract from JSON-LD structured data (common in news sites)
        if not cleaned or len('\n\n'.join(cleaned)) < 200:
            json_ld_matches = re.findall(r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>', text, flags=re.IGNORECASE)
            for json_ld in json_ld_matches:
                try:
                    import json
                    data = json.loads(json_ld)
                    # Extract articleBody or description
                    if isinstance(data, dict):
                        if 'articleBody' in data:
                            cleaned.append(data['articleBody'])
                        if 'description' in data:
                            cleaned.append(data['description'])
                        if 'headline' in data:
                            cleaned.append(data['headline'])
                except:
                    pass
        
        # Strategy 4: Extract from meta tags (og:description, description, etc.)
        if not cleaned or len('\n\n'.join(cleaned)) < 200:
            meta_patterns = [
                r'<meta[^>]*property=["\']og:description["\'][^>]*content=["\']([^"\']+)["\']',
                r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']',
                r'<meta[^>]*name=["\']twitter:description["\'][^>]*content=["\']([^"\']+)["\']',
            ]
            for pattern in meta_patterns:
                matches = re.findall(pattern, text, flags=re.IGNORECASE)
                for match in matches:
                    desc = html.unescape(match).strip()
                    if desc and len(desc) > 50:
                        cleaned.append(desc)
        
        # Strategy 5: Extract all paragraphs from body 
        if not cleaned:
            paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", text, flags=re.IGNORECASE)
            for p in paragraphs[:50]: 
                p_txt = re.sub(r"<[^>]+>", " ", p)
                p_txt = html.unescape(p_txt)
                p_txt = re.sub(r"\s+", " ", p_txt).strip()
                # Filter out navigation, footer, etc.
                if p_txt and len(p_txt) > 30 and not any(skip in p_txt.lower() for skip in ['cookie', 'privacy', 'terms', 'subscribe', 'newsletter']):
                    cleaned.append(p_txt)
        
        # Strategy 6: Last resort - extract text from body tag
        if not cleaned or len('\n\n'.join(cleaned)) < 200:
            body_match = re.search(r"<body[^>]*>([\s\S]*?)</body>", text, flags=re.IGNORECASE)
            if body_match:
                body_text = body_match.group(1)
                # Remove all HTML tags
                body_text = re.sub(r"<[^>]+>", " ", body_text)
                body_text = html.unescape(body_text)
                body_text = re.sub(r"\s+", " ", body_text).strip()
                # Split into sentences
                sentences = re.split(r'[.!?]+\s+', body_text)
                for sent in sentences[:100]:
                    sent = sent.strip()
                    if sent and len(sent) > 50:
                        cleaned.append(sent)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_cleaned = []
        for item in cleaned:
            item_lower = item.lower().strip()
            if item_lower and item_lower not in seen and len(item) > 20:
                seen.add(item_lower)
                unique_cleaned.append(item)
        
        fetched_text = "\n\n".join(unique_cleaned)
        
        # Limit length
        if len(fetched_text) > max_length:
            fetched_text = fetched_text[:max_length]
        
        if fetched_text.strip():
            logger.info(f"Successfully fetched {len(fetched_text)} characters from URL: {url[:50]}...")
            return fetched_text.strip()
        else:
            logger.warning(f"No content extracted from URL: {url}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to fetch URL content from {url}: {e}")
        return None

def is_url(text: str) -> bool:
    """Check if text is a URL"""
    if not text or not isinstance(text, str):
        return False
    text = text.strip()
    return text.startswith(('http://', 'https://')) and len(text) > 10

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
    image_url_or_b64: Optional[str] = None

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
    
class UrlFetchRequest(BaseModel):
    url: str

class BatchGenerationRequest(BaseModel):
    topics: List[str]
    samples_per_topic: Optional[int] = 5
    strategies: Optional[List[str]] = None


@app.post("/api/url/fetch")
async def fetch_url_endpoint(request: UrlFetchRequest):
    """Fetch raw text from a URL without running detection."""
    url = request.url.strip()
    if not is_url(url):
        raise HTTPException(status_code=400, detail="Invalid URL provided")
    
    content = fetch_url_content(url)
    if not content:
        raise HTTPException(status_code=422, detail="Failed to fetch content from URL")
    
    return {
        "success": True,
        "fetched_content": content,
        "original_url": url
    }

# ============ Auth models ============
class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    avatar_url_or_b64: Optional[str] = None

class LoginRequest(BaseModel):
    username_or_email: str
    password: str

class FirebaseSyncRequest(BaseModel):
    uid: str
    email: Optional[EmailStr] = None
    display_name: Optional[str] = None
    avatar_url_or_b64: Optional[str] = None

class UpdateAvatarRequest(BaseModel):
    uid: Optional[str] = None
    username_or_email: Optional[str] = None
    avatar_url_or_b64: str

class UpdateProfileRequest(BaseModel):
    uid: Optional[str] = None
    username_or_email: Optional[str] = None
    username: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url_or_b64: Optional[str] = None

# ============ Vision describe models ============
class VisionDescribeRequest(BaseModel):
    image_url_or_b64: str
    detail_level: Optional[str] = "high"  # "low" | "high" | "auto"
    additional_prompt: Optional[str] = None
    output_mode: Optional[str] = "detailed"  # "detailed" | "concise"
    max_chars: Optional[int] = None  # None or <=0 means no truncation

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

def get_news_service():
    return NewsService()

def get_vision_service():
    """Lazy init VisionService for image understanding"""
    global vision_service
    if vision_service is None:
        from services.vision_service import VisionService
        vision_service = VisionService()
    return vision_service

# API routes
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    global detection_service, improved_detection, generation_service, vision_service
    
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
    vision_service = None
    
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

# ============ Vision endpoints ============
@app.post("/api/vision/describe")
async def vision_describe(
    body: VisionDescribeRequest,
    vision: Any = Depends(get_vision_service),
    http_request: Request = None
):
    try:
        res = vision.describe_image(
            image_url_or_b64=body.image_url_or_b64,
            detail_level=body.detail_level or "high",
            additional_prompt=body.additional_prompt,
            output_mode=body.output_mode or "detailed",
            max_chars=(body.max_chars if (body.max_chars is not None) else None)
        )
        # activity log (best-effort)
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "vision_describe",
                    "user": {},
                    "request_meta": {
                        "image_provided": bool(body.image_url_or_b64),
                        "image_url_or_b64": body.image_url_or_b64,
                        "detail_level": body.detail_level or "high"
                    },
                    "result_meta": {
                        "ok": bool(res.get("success")),
                        "error": res.get("error")
                    },
                    "client": _client_info(http_request),
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

        return res
    except Exception as e:
        logger.error(f"Vision describe error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
        "avatar_url_or_b64": body.avatar_url_or_b64 or None,
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
    access_token = create_access_token(
        str(inserted.inserted_id),
        additional_claims={
            "username": body.username,
            "email": str(body.email),
        },
    )
    return {
        "success": True,
        "user_id": str(inserted.inserted_id),
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }

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
    if not user.get("is_active", True):
        raise HTTPException(status_code=403, detail="User account is inactive")
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
    access_token = create_access_token(
        str(user["_id"]),
        additional_claims={
            "username": user.get("username"),
            "email": user.get("email"),
        },
    )
    return {
        "success": True,
        "username": user.get("username"),
        "email": user.get("email"),
        "user_id": str(user["_id"]),
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }


@app.get("/api/auth/me")
async def get_me(current_user: Dict[str, Any] = Depends(require_active_user)):
    """Return the authenticated user's profile."""
    return {
        "success": True,
        "user": {
            "user_id": str(current_user.get("_id", current_user.get("id"))),
            "username": current_user.get("username"),
            "email": current_user.get("email"),
            "display_name": current_user.get("display_name"),
            "avatar_url_or_b64": current_user.get("avatar_url_or_b64"),
            "role": current_user.get("role", "user"),
            "is_active": current_user.get("is_active", True),
            "created_at": current_user.get("created_at"),
            "last_login_at": current_user.get("last_login_at"),
        },
    }

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
            "avatar_url_or_b64": body.avatar_url_or_b64 if body.avatar_url_or_b64 else None,
            "is_active": True,
            "updated_at": datetime.utcnow().isoformat()
        },
        "$setOnInsert": {
            "created_at": datetime.utcnow().isoformat(),
            "role": "user"
        }
    }
    res = users.update_one(key_filter, update_doc, upsert=True)
    # Get the user document to retrieve user_id
    user_doc = users.find_one(key_filter)
    user_id = str(user_doc["_id"]) if user_doc else None
    
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
    
    # Generate access token for the user
    if user_id:
        access_token = create_access_token(
            user_id,
            additional_claims={
                "username": body.display_name or body.email or body.uid,
                "email": str(body.email) if body.email else None,
            },
        )
        return {
            "success": True,
            "upserted": bool(res.upserted_id),
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": Config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        }
    return {"success": True, "upserted": bool(res.upserted_id)}

@app.post("/api/auth/update_avatar")
async def update_avatar(body: UpdateAvatarRequest, request: Request):
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    if not body.avatar_url_or_b64:
        raise HTTPException(status_code=422, detail="avatar_url_or_b64 is required")
    users = mongo_service.get_collection("users")
    # Identify user
    query = None
    if body.uid:
        query = {"uid": body.uid}
    elif body.username_or_email:
        query = {"$or": [{"username": body.username_or_email}, {"email": body.username_or_email}]}
    else:
        raise HTTPException(status_code=422, detail="Provide uid or username_or_email")
    user = users.find_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    users.update_one(query, {"$set": {"avatar_url_or_b64": body.avatar_url_or_b64, "updated_at": datetime.utcnow().isoformat()}}, bypass_document_validation=True)
    try:
        if mongo_service.is_connected():
            mongo_service.insert_one("user_activity_log", {
                "action": "update_avatar",
                "user": {"uid": user.get("uid"), "username": user.get("username"), "email": user.get("email")},
                "request_meta": {"avatar_provided": True},
                "result_meta": {"ok": True},
                "client": _client_info(request),
                "created_at": datetime.utcnow().isoformat()
            })
    except Exception:
        pass
    return {"success": True}

@app.put("/api/auth/update_profile")
async def update_profile(body: UpdateProfileRequest, request: Request):
    """
    Update a user's profile information.
    
    The user can be identified by uid or username/email.
    Supported fields:
    - username/display_name
    - email
    - avatar_url_or_b64
    
    Args:
        body: Request payload containing the identifier and fields to update
    
    Returns:
        Update result
    """
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    users = mongo_service.get_collection("users")
    
    # Determine which identifier is provided (uid first, then username/email)
    query = None
    if body.uid:
        query = {"uid": body.uid}
    elif body.username_or_email:
        query = {"$or": [{"username": body.username_or_email}, {"email": body.username_or_email}]}
    else:
        raise HTTPException(status_code=422, detail="Provide uid or username_or_email to identify user")
    
    # Verify user exists
    user = users.find_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Build update document
    update_doc: Dict[str, Any] = {
        "$set": {
            "updated_at": datetime.utcnow().isoformat()
        }
    }
    
    # Track whether any field is actually updated
    has_updates = False
    
    # Update username/display name, preferring display_name when provided
    if body.display_name is not None:
        update_doc["$set"]["display_name"] = body.display_name
        # If username is missing, mirror the display_name
        if not user.get("username"):
            update_doc["$set"]["username"] = body.display_name
        has_updates = True
    elif body.username is not None:
        update_doc["$set"]["username"] = body.username
        # If display_name is missing, mirror the username
        if not user.get("display_name"):
            update_doc["$set"]["display_name"] = body.username
        has_updates = True
    
    # Update email
    if body.email is not None:
        # Ensure no other user already owns the email
        existing_user = users.find_one({"email": str(body.email), "_id": {"$ne": user.get("_id")}})
        if existing_user:
            raise HTTPException(status_code=409, detail="Email already in use by another user")
        update_doc["$set"]["email"] = str(body.email)
        has_updates = True
    
    # Update avatar
    if body.avatar_url_or_b64 is not None:
        update_doc["$set"]["avatar_url_or_b64"] = body.avatar_url_or_b64
        has_updates = True
    
    if not has_updates:
        raise HTTPException(status_code=422, detail="No fields provided for update")
    
    # Execute update
    try:
        result = users.update_one(query, update_doc, bypass_document_validation=True)
        if result.modified_count == 0 and result.matched_count > 0:
            # Treat identical values as success
            pass
        elif result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Record activity log
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "update_profile",
                    "user": {
                        "uid": user.get("uid"),
                        "username": user.get("username"),
                        "email": user.get("email")
                    },
                    "request_meta": {
                        "updated_fields": list(update_doc["$set"].keys())
                    },
                    "result_meta": {"ok": True},
                    "client": _client_info(request),
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass
        
        return {
            "success": True,
            "message": "Profile updated successfully",
            "updated_fields": list(update_doc["$set"].keys())
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")

# Detection endpoints
@app.post("/api/detect/baseline")
async def baseline_detection(
    request: DetectionRequest,
    service: Any = Depends(get_detection_service),
    vision: Any = Depends(get_vision_service),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_active_user),
    http_request: Request = None
):
    """Baseline detection"""
    try:
        logger.info(f"Baseline detection request for text: {request.text[:100]}...")
        user_object_id = _current_user_object_id(current_user) if current_user else None
        user_summary = {
            "id": str(user_object_id) if user_object_id else None,
            "username": current_user.get("username") if current_user else None,
            "email": current_user.get("email") if current_user else None,
        }
        # Auto fetch URL content if text is a URL
        req_text = (request.text or '').strip()
        if is_url(req_text):
            logger.info(f"Detected URL input, fetching content from: {req_text[:80]}...")
            try:
                fetched_content = fetch_url_content(req_text)
                if fetched_content:
                    req_text = fetched_content
                    logger.info(f"Successfully fetched {len(req_text)} characters from URL")
                else:
                    logger.warning(f"Failed to extract content from URL (may be JavaScript-rendered). Using URL as text for detection.")
                    # Keep URL as text - detection can still work with URL
            except Exception as e:
                logger.error(f"Error fetching URL content: {e}. Using URL as text for detection.")
                # Keep URL as text - detection can still work with URL
        
        # Auto-generate description from image if text is empty
        if (not req_text) and request.image_url_or_b64:
            try:
                vision_res = vision.describe_image(request.image_url_or_b64, detail_level="high")
                if vision_res.get("success") and vision_res.get("description"):
                    req_text = vision_res["description"][:1000]
                    logger.info("Image description generated for baseline detection.")
                else:
                    logger.warning(f"Vision description failed: {vision_res.get('error')}")
            except Exception as e:
                logger.warning(f"Vision service error (baseline): {e}")
        
        result = service.baseline_detection(
            text=req_text or request.text,
            image_url_or_b64=request.image_url_or_b64
        )
        # Write to MongoDB (best-effort)
        inserted_id = None
        try:
            if mongo_service.is_connected():
                inserted_id = mongo_service.insert_one("detection_results", {
                    "type": "baseline",
                    "text": req_text or request.text,
                    "image_url_or_b64": request.image_url_or_b64,
                    "result": result,
                    "created_at": datetime.utcnow().isoformat(),
                    "user_id": user_object_id,
                })
                
                # Generate PDF if auto-generate is enabled
                if Config.PDF_AUTO_GENERATE and inserted_id:
                    try:
                        detection_data = {
                            "type": "baseline",
                            "text": req_text or request.text,
                            "image_url_or_b64": request.image_url_or_b64,
                            "result": result,
                            "created_at": datetime.utcnow().isoformat()
                        }
                        pdf_info = pdf_service.generate_detection_pdf(inserted_id, detection_data)
                        if pdf_info:
                            # Update record with PDF paths
                            col = mongo_service.get_collection("detection_results")
                            col.update_one(
                                {"_id": ObjectId(inserted_id)},
                                {"$set": {"pdf_path": pdf_info["pdf_path"], "pdf_url": pdf_info["pdf_url"]}}
                            )
                    except Exception as pdf_error:
                        logger.warning(f"Failed to generate PDF for detection {inserted_id}: {pdf_error}")
        except Exception:
            pass

        # activity log (store input text and full result for audit)
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "detect_baseline",
                    "user": user_summary,
                    "request_meta": {
                        "text_preview": (req_text or request.text)[:300],
                        "image_provided": bool(request.image_url_or_b64),
                        "image_url_or_b64": request.image_url_or_b64 or None
                    },
                    "result_meta": {
                        "ok": True,
                        "result": result  # store full detection result
                    },
                    "client": _client_info(http_request),
                    "created_at": datetime.utcnow().isoformat()
                })
        except Exception:
            pass

        return {
            "success": True,
            "result": result,
            "record_id": str(inserted_id) if inserted_id else None,
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
    vision: Any = Depends(get_vision_service),
    current_user: Optional[Dict[str, Any]] = Depends(get_optional_active_user),
    http_request: Request = None
):
    """Improved detection with customizable configuration"""
    try:
        logger.info(f"Improved detection request for text: {request.text[:100]}...")
        # Auto fetch URL content if text is a URL
        req_text = (request.text or '').strip()
        if is_url(req_text):
            logger.info(f"Detected URL input, fetching content from: {req_text[:80]}...")
            try:
                fetched_content = fetch_url_content(req_text)
                if fetched_content:
                    req_text = fetched_content
                    logger.info(f"Successfully fetched {len(req_text)} characters from URL")
                else:
                    logger.warning(f"Failed to extract content from URL (may be JavaScript-rendered). Using URL as text for detection.")
                    # Keep URL as text - detection can still work with URL
            except Exception as e:
                logger.error(f"Error fetching URL content: {e}. Using URL as text for detection.")
                # Keep URL as text - detection can still work with URL
        
        # Auto image description if text empty and image provided
        if (not req_text) and request.image_url_or_b64:
            try:
                vision_res = vision.describe_image(request.image_url_or_b64, detail_level="high")
                if vision_res.get("success") and vision_res.get("description"):
                    req_text = vision_res["description"][:1000]
                    logger.info("Image description generated for improved detection.")
                else:
                    logger.warning(f"Vision description failed: {vision_res.get('error')}")
            except Exception as e:
                logger.warning(f"Vision service error (improved): {e}")
        
        # Extract custom configuration
        config = request.detection_config.dict() if request.detection_config else {}
        logger.info(f"Detection configuration: {config}")
        user_object_id = _current_user_object_id(current_user) if current_user else None
        user_summary = {
            "id": str(user_object_id) if user_object_id else None,
            "username": current_user.get("username") if current_user else None,
            "email": current_user.get("email") if current_user else None,
        }
        
        if request.use_improved_detection:
            # Execute baseline detection
            baseline_results = detection_service.baseline_detection(
                text=req_text or request.text,
                image_url_or_b64=request.image_url_or_b64
            )
            
            # Execute improved detection with custom config
            improved_results = improved_service.improved_detection(
                baseline_results=baseline_results,
                text=req_text or request.text,
                image_metadata=None,  # Can be extended with image metadata
                detection_config=config  # NEW: Pass custom configuration
            )
            # Write to MongoDB (best-effort)
            inserted_id = None
            try:
                if mongo_service.is_connected():
                    inserted_id = mongo_service.insert_one("detection_results", {
                        "type": "improved",
                        "text": req_text or request.text,
                        "image_url_or_b64": request.image_url_or_b64,
                        "config": config,
                        "baseline": baseline_results,
                        "result": improved_results,
                        "created_at": datetime.utcnow().isoformat(),
                        "user_id": user_object_id,
                    })

                    # Generate PDF if auto-generate is enabled
                    if Config.PDF_AUTO_GENERATE and inserted_id:
                        try:
                            detection_data = {
                                "type": "improved",
                                "text": req_text or request.text,
                                "image_url_or_b64": request.image_url_or_b64,
                                "config": config,
                                "baseline": baseline_results,
                                "result": improved_results,
                                "created_at": datetime.utcnow().isoformat()
                            }
                            pdf_info = pdf_service.generate_detection_pdf(inserted_id, detection_data)
                            if pdf_info:
                                # Update record with PDF paths
                                col = mongo_service.get_collection("detection_results")
                                col.update_one(
                                    {"_id": ObjectId(inserted_id)},
                                    {"$set": {"pdf_path": pdf_info["pdf_path"], "pdf_url": pdf_info["pdf_url"]}}
                                )
                        except Exception as pdf_error:
                            logger.warning(f"Failed to generate PDF for detection {inserted_id}: {pdf_error}")
            except Exception:
                pass

            # activity log (store input text and full improved result for audit)
            try:
                if mongo_service.is_connected():
                    mongo_service.insert_one("user_activity_log", {
                        "action": "detect_improved",
                        "user": user_summary,
                    "request_meta": {
                            "text_preview": (req_text or request.text)[:300],
                            "use_improved": True,
                            "image_provided": bool(request.image_url_or_b64),
                            "image_url_or_b64": request.image_url_or_b64 or None
                        },
                        "result_meta": {
                            "ok": True,
                            "result": improved_results  # store full improved detection result
                        },
                        "client": _client_info(http_request),
                        "created_at": datetime.utcnow().isoformat()
                    })
            except Exception:
                pass

            response_data = {
                "success": True,
                "result": improved_results,
                "record_id": str(inserted_id) if inserted_id else None,
                "timestamp": datetime.now().isoformat()
            }
            # If URL was fetched, include the fetched content in response
            if is_url(request.text) and req_text != request.text:
                response_data["fetched_content"] = req_text[:5000]  # Include first 5000 chars
                response_data["original_url"] = request.text
            
            return response_data
        else:
            # Use baseline detection only
            result = detection_service.baseline_detection(
                text=req_text or request.text,
                image_url_or_b64=request.image_url_or_b64
            )
            
            # activity log (baseline-only path, store full result)
            try:
                if mongo_service.is_connected():
                    mongo_service.insert_one("user_activity_log", {
                        "action": "detect_baseline",
                        "user": user_summary,
                    "request_meta": {
                            "text_preview": (req_text or request.text)[:300],
                            "image_provided": bool(request.image_url_or_b64),
                            "image_url_or_b64": request.image_url_or_b64 or None
                        },
                        "result_meta": {
                            "ok": True,
                            "result": result
                        },
                        "client": _client_info(http_request),
                        "created_at": datetime.utcnow().isoformat()
                    })
            except Exception:
                pass

            return {
                "success": True,
                "result": result,
                "record_id": str(inserted_id) if inserted_id else None,
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
    news_service: Any = Depends(get_news_service),
    vision: Any = Depends(get_vision_service),
    http_request: Request = None,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    """Generate single fake news sample - automatically searches for real news and generates based on it"""
    try:
        logger.info(f"Generation request for topic: {request.topic}")
        user_object_id = current_user["_id"]     
        user_summary = {
            "username": current_user.get("username"),
            "email": current_user.get("email")
        }
        # If topic empty but image provided, auto generate topic from image
        req_topic_override = None
        if (not (request.topic or '').strip()) and getattr(request, 'image_url_or_b64', None):
            try:
                vision_res = vision.describe_image(
                    request.image_url_or_b64,
                    detail_level="high",
                    additional_prompt="Please rewrite the first sentence of the summary as a concise, news-style headline."
                )
                if vision_res.get("success") and vision_res.get("description"):
                    first_line = vision_res["description"].splitlines()[0].strip()
                    req_topic_override = first_line[:120] if first_line else vision_res["description"][:120]
                    logger.info("Image description generated for generation topic.")
                else:
                    logger.warning(f"Vision description failed (generation): {vision_res.get('error')}")
            except Exception as e:
                logger.warning(f"Vision service error (generation): {e}")
        
        # Extract style, domain, and actual topic from the prompt
        # Format: "Write a {topic} news article in a {tone} tone about: {baseTopic}"
        topic_text = req_topic_override if req_topic_override else request.topic
        prompt_lower = topic_text.lower()
        
        # Parse style/tone from prompt - more precise matching
        style = None
        # Direct matching for tones
        if "in a formal tone" in prompt_lower or "formal —" in prompt_lower:
            style = "formal"
        elif "in a sensational tone" in prompt_lower or "sensational —" in prompt_lower:
            style = "sensational"
        elif "in a fun tone" in prompt_lower or "fun —" in prompt_lower:
            style = "fun"
        elif "in a normal tone" in prompt_lower or "normal —" in prompt_lower:
            style = "normal"
        else:
            # Fallback keyword matching
            tone_patterns = {
                "formal": ["formal", "professional", "neutral", "authoritative"],
                "sensational": ["sensational", "dramatic", "emotional"],
                "fun": ["fun", "playful", "humorous", "light-hearted"],
                "normal": ["normal", "natural", "everyday"]
            }
            for style_key, keywords in tone_patterns.items():
                if any(kw in prompt_lower for kw in keywords):
                    style = style_key
                    break
        
        # Parse domain/topic from prompt - more precise matching
        domain = None
        # Direct matching for topics
        if "write a politics" in prompt_lower or "politics —" in prompt_lower:
            domain = "politics"
        elif "write a business" in prompt_lower or "business —" in prompt_lower:
            domain = "business"
        elif "write a sports" in prompt_lower or "sports —" in prompt_lower:
            domain = "sports"
        elif "write a technology" in prompt_lower or "technology —" in prompt_lower:
            domain = "technology"
        elif "write a general" in prompt_lower or "general —" in prompt_lower:
            domain = None  # General means no specific domain
        else:
            # Fallback keyword matching
            domain_patterns = {
                "politics": ["politics", "political", "government", "election"],
                "business": ["business", "market", "economic", "company"],
                "sports": ["sports", "sport", "athlete", "game"],
                "technology": ["technology", "tech", "digital", "innovation"]
            }
            for domain_key, keywords in domain_patterns.items():
                if any(kw in prompt_lower for kw in keywords):
                    domain = domain_key
                    break
        
        # Extract the actual search query from the prompt
        if "about: " in topic_text:
            topic_text = topic_text.split("about: ")[-1].strip()
        else:
            # Try to extract from other patterns
            import re
            match = re.search(r"about\s*:\s*(.+)$", topic_text, re.IGNORECASE)
            if match:
                topic_text = match.group(1).strip()
        
        # Check if topic looks like a URL
        is_url = False
        try:
            from urllib.parse import urlparse
            parsed = urlparse(topic_text)
            is_url = bool(parsed.scheme and parsed.netloc)
        except:
            pass
        
        source_url = None
        source_text = None
        
        if is_url:
            # If input is a URL, fetch content from it
            try:
                import urllib.request
                import re
                import html
                req = urllib.request.Request(topic_text, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = resp.read()
                text = raw.decode("utf-8", errors="ignore")
                text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
                text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
                article_match = re.search(r"<article[\s\S]*?</article>", text, flags=re.IGNORECASE)
                candidate = article_match.group(0) if article_match else text
                paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", candidate, flags=re.IGNORECASE)
                cleaned = []
                for p in paragraphs[:20]:
                    p_txt = re.sub(r"<[^>]+>", " ", p)
                    p_txt = html.unescape(p_txt)
                    p_txt = re.sub(r"\s+", " ", p_txt).strip()
                    if p_txt:
                        cleaned.append(p_txt)
                source_text = "\n\n".join(cleaned)
                source_url = topic_text
                if not source_text:
                    source_text = "Article content unavailable"
            except Exception as e:
                logger.warning(f"Failed to fetch content from URL: {e}")
                source_text = "Article content unavailable"
                source_url = topic_text
        else:
            # Search for real news articles using News API
            try:
                news = news_service.search_news(query=topic_text, language="en", page_size=3)
                articles = (news or {}).get("articles") or []
                
                if articles and articles[0].get("url"):
                    article = articles[0]
                    source_url = article.get("url", "")
                    title = article.get("title", "")
                    desc = article.get("description", "")
                    source_text = (title + "\n\n" + desc).strip()
                    
                    # Try to fetch full content
                    try:
                        import urllib.request
                        import re
                        import html
                        req = urllib.request.Request(source_url, headers={"User-Agent": "Mozilla/5.0"})
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            raw = resp.read()
                        text = raw.decode("utf-8", errors="ignore")
                        text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
                        text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
                        article_match = re.search(r"<article[\s\S]*?</article>", text, flags=re.IGNORECASE)
                        candidate = article_match.group(0) if article_match else text
                        paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", candidate, flags=re.IGNORECASE)
                        cleaned = []
                        for p in paragraphs[:20]:
                            p_txt = re.sub(r"<[^>]+>", " ", p)
                            p_txt = html.unescape(p_txt)
                            p_txt = re.sub(r"\s+", " ", p_txt).strip()
                            if p_txt:
                                cleaned.append(p_txt)
                        if cleaned:
                            source_text = "\n\n".join(cleaned)
                    except Exception:
                        pass  # Use title + description if full content fetch fails
            except Exception as e:
                logger.warning(f"Failed to search news: {e}")
        
        def infer_domain_style_from_text(text: str) -> Tuple[Optional[str], Optional[str]]:
            if not text:
                return None, None
            text_lower = text.lower()

            domain_keywords: Dict[str, List[Tuple[str, float]]] = {
                "politics": [
                    ("government", 1.5), ("election", 1.7), ("policy", 1.1), ("president", 1.4),
                    ("minister", 1.2), ("parliament", 1.4), ("congress", 1.4), ("senate", 1.2),
                    ("campaign", 1.1), ("diplomatic", 1.1), ("bill", 0.8), ("legislation", 1.2)
                ],
                "business": [
                    ("market", 1.4), ("economy", 1.3), ("finance", 1.3), ("company", 1.0),
                    ("startup", 1.0), ("investment", 1.2), ("revenue", 1.3), ("profit", 1.3),
                    ("corporate", 1.1), ("stock", 1.2), ("merger", 1.2), ("shareholder", 1.2),
                    ("earnings", 1.3), ("quarter", 0.9)
                ],
                "sports": [
                    ("match", 1.2), ("game", 1.0), ("tournament", 1.4), ("league", 1.3),
                    ("player", 1.0), ("coach", 1.0), ("season", 1.1), ("score", 1.0),
                    ("championship", 1.5), ("olympic", 1.5), ("victory", 1.1), ("defeat", 1.1),
                    ("goal", 1.0), ("playoff", 1.3)
                ],
                "technology": [
                    ("technology", 1.3), ("tech", 1.3), ("software", 1.2), ("hardware", 1.2),
                    ("ai", 1.5), ("artificial intelligence", 1.7), ("robot", 1.1),
                    ("digital", 1.0), ("cyber", 1.2), ("innovation", 1.2), ("cloud", 1.1),
                    ("startup", 1.0), ("algorithm", 1.3), ("data", 1.0)
                ],
                "health": [
                    ("hospital", 1.2), ("vaccine", 1.5), ("disease", 1.3), ("health", 1.1),
                    ("medical", 1.3), ("doctor", 1.2), ("patients", 1.1), ("virus", 1.4),
                    ("nutrition", 1.0), ("therapy", 1.1), ("clinical", 1.2), ("public health", 1.4)
                ],
                "environment": [
                    ("climate", 1.4), ("environment", 1.2), ("wildfire", 1.6), ("sustainability", 1.2),
                    ("pollution", 1.3), ("ecosystem", 1.2), ("emissions", 1.3), ("renewable", 1.1),
                    ("conservation", 1.2), ("carbon", 1.1), ("earthquake", 1.3), ("flood", 1.3)
                ],
                "science": [
                    ("research", 1.2), ("scientists", 1.3), ("study", 1.2), ("laboratory", 1.1),
                    ("discovered", 1.2), ("experiment", 1.1), ("NASA", 1.3), ("space", 1.1),
                    ("astronomy", 1.3), ("physics", 1.2), ("biology", 1.2), ("university", 0.9)
                ],
                "crime": [
                    ("investigation", 1.2), ("suspect", 1.2), ("police", 1.1), ("fraud", 1.3),
                    ("arrested", 1.2), ("charges", 1.1), ("lawsuit", 1.1), ("security breach", 1.4),
                    ("corruption", 1.2)
                ],
                "entertainment": [
                    ("festival", 1.3), ("film", 1.1), ("movie", 1.1), ("celebrity", 1.2),
                    ("concert", 1.3), ("award", 1.2), ("music", 1.1), ("series", 1.0),
                    ("premiere", 1.2), ("hollywood", 1.4), ("box office", 1.3)
                ],
            }

            sensational_keywords = [
                "breaking", "crisis", "disaster", "urgent", "scandal", "shocking",
                "attack", "protest", "violence", "alert", "storm", "emergency",
                "explosion", "tragedy", "wildfire", "threatens"
            ]
            fun_keywords = [
                "festival", "celebration", "party", "music", "concert", "holiday",
                "comedy", "event", "kids", "fun", "entertainment", "parade", "picnic"
            ]

            domain_scores: Dict[str, float] = {key: 0.0 for key in domain_keywords}
            for domain_key, keywords in domain_keywords.items():
                for keyword, weight in keywords:
                    if keyword in text_lower:
                        domain_scores[domain_key] += weight

            best_domain = max(domain_scores, key=domain_scores.get)
            inferred_domain = best_domain if domain_scores[best_domain] >= 1.0 else None

            inferred_style: Optional[str]
            style_scores: Dict[str, float] = {
                "sensational": 0.0,
                "fun": 0.0,
                "formal": 0.0,
                "normal": 0.0,
            }

            for kw in sensational_keywords:
                if kw in text_lower:
                    style_scores["sensational"] += 1.2
            style_scores["sensational"] += text_lower.count("!") * 0.4
            if "breaking news" in text_lower:
                style_scores["sensational"] += 1.0

            for kw in fun_keywords:
                if kw in text_lower:
                    style_scores["fun"] += 1.1
            if "festival" in text_lower or "celebration" in text_lower:
                style_scores["fun"] += 0.6

            formal_markers = [
                ("according to", 1.0), ("official", 0.8), ("statement", 0.7),
                ("report", 0.8), ("conference", 0.7), ("authorities", 0.9),
                ("analysis", 0.8), ("research", 0.8)
            ]
            for kw, weight in formal_markers:
                if kw in text_lower:
                    style_scores["formal"] += weight
            if inferred_domain in {"politics", "business", "science"}:
                style_scores["formal"] += 0.6

            neutral_markers = [
                ("community", 0.4), ("local", 0.4), ("everyday", 0.3),
                ("routine", 0.3), ("update", 0.3)
            ]
            for kw, weight in neutral_markers:
                if kw in text_lower:
                    style_scores["normal"] += weight

            best_style = max(style_scores, key=style_scores.get)
            if style_scores[best_style] < 0.6:
                inferred_style = "normal"
            else:
                inferred_style = best_style

            return inferred_domain, inferred_style

        combined_text_for_inference = " ".join(
            filter(None, [topic_text, source_text])
        )
        inferred_domain, inferred_style = infer_domain_style_from_text(combined_text_for_inference)

        if not domain and inferred_domain:
            domain = inferred_domain
            logger.info(f"Inferred domain from content: {domain}")
        if not style and inferred_style:
            style = inferred_style
            logger.info(f"Inferred style from content: {style}")

        # Prepare request_dict for MongoDB storage (used in both branches)
        request_dict = request.dict()
        if req_topic_override:
            request_dict["topic"] = req_topic_override
        if style:
            request_dict["style"] = style
        if domain:
            request_dict["domain"] = domain
        
        # If we found a source URL, generate from real news with style and domain
        if source_url and source_text:
            logger.info(f"Generating from real news: {source_url} (style={style}, domain={domain})")
            result = service.generate_from_real({
                "source_text": source_text,
                "source_url": source_url,
                "strategy": "loaded_language",
                "model_type": "gpt-4o",
                "style": style,
                "domain": domain
            })
        else:
            # Fallback to original generation method with style and domain
            result = service.generate_fake_news(request_dict)
        
        # Write to MongoDB (best-effort)
        inserted_id = None
        try:
            if mongo_service.is_connected():
                # Ensure strategy is set (required by MongoDB validator)
                strategy_value = request.strategy if request.strategy else "loaded_language"
                generation_doc = {
                    "topic": req_topic_override or request.topic,
                    "strategy": strategy_value,
                    "model_type": request.model_type,
                    "image_url_or_b64": getattr(request, 'image_url_or_b64', None),
                    "params": request_dict,
                    "result": result,
                    "created_at": datetime.utcnow().isoformat(),
                    "user_id": user_object_id,
                }
                if user_object_id is not None:
                    generation_doc["user_id"] = user_object_id
                inserted_id = mongo_service.insert_one("generation_results", generation_doc)
                logger.info(f"Successfully saved generation result to MongoDB")
                
                # Generate PDF if auto-generate is enabled
                if Config.PDF_AUTO_GENERATE and inserted_id:
                    try:
                        generation_data = {
                            "topic": req_topic_override or request.topic,
                            "strategy": strategy_value,
                            "model_type": request.model_type,
                            "image_url_or_b64": getattr(request, 'image_url_or_b64', None),
                            "params": request_dict,
                            "result": result,
                            "created_at": datetime.utcnow().isoformat()
                        }
                        pdf_info = pdf_service.generate_generation_pdf(inserted_id, generation_data)
                        if pdf_info:
                            # Update record with PDF paths
                            col = mongo_service.get_collection("generation_results")
                            col.update_one(
                                {"_id": ObjectId(inserted_id)},
                                {"$set": {"pdf_path": pdf_info["pdf_path"], "pdf_url": pdf_info["pdf_url"]}}
                            )
                    except Exception as pdf_error:
                        logger.warning(f"Failed to generate PDF for generation {inserted_id}: {pdf_error}")
        except Exception as e:
            logger.error(f"Failed to save generation result to MongoDB: {e}")
            pass

        # activity log (store generated article for audit)
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "generate_single",
                    "user": user_summary or {},
                    "request_meta": {
                        "topic": req_topic_override or request.topic,
                        "strategy": request.strategy,
                        "image_provided": bool(getattr(request, 'image_url_or_b64', None)),
                        "image_url_or_b64": getattr(request, 'image_url_or_b64', None)
                    },
                    "result_meta": {
                        "ok": True,
                        "article": (result.get("article") if isinstance(result, dict) else None),
                        "result": result
                    },
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
    current_user: Dict[str, Any] = Depends(require_active_user),
    http_request: Request = None
):
    """Batch generate fake news samples"""
    try:
        logger.info(f"Batch generation request for {len(request.topics)} topics")
        user_object_id = _current_user_object_id(current_user)
        user_summary = {
            "id": str(user_object_id),
            "username": current_user.get("username"),
            "email": current_user.get("email"),
        }
        
        results = service.generate_batch(
            topics=request.topics,
            strategy=request.strategies[0] if request.strategies else None,
            samples_per_topic=request.samples_per_topic or 1
        )
        # Write to MongoDB (best-effort)
        try:
            if mongo_service.is_connected():
                for r in results:
                    inserted_id = mongo_service.insert_one("generation_results", {
                        "topic": r.get("topic"),
                        "strategy": r.get("strategy"),
                        "model_type": r.get("model"),
                        "params": {"strategy": request.strategies[0] if request.strategies else None, "samples_per_topic": request.samples_per_topic or 1},
                        "result": r,
                        "created_at": datetime.utcnow().isoformat(),
                        "user_id": user_object_id,
                    })
                    
                    # Generate PDF if auto-generate is enabled
                    if Config.PDF_AUTO_GENERATE and inserted_id:
                        try:
                            generation_data = {
                                "topic": r.get("topic"),
                                "strategy": r.get("strategy"),
                                "model_type": r.get("model"),
                                "params": {"strategy": request.strategies[0] if request.strategies else None, "samples_per_topic": request.samples_per_topic or 1},
                                "result": r,
                                "created_at": datetime.utcnow().isoformat()
                            }
                            pdf_info = pdf_service.generate_generation_pdf(inserted_id, generation_data)
                            if pdf_info:
                                col = mongo_service.get_collection("generation_results")
                                col.update_one(
                                    {"_id": ObjectId(inserted_id)},
                                    {"$set": {"pdf_path": pdf_info["pdf_path"], "pdf_url": pdf_info["pdf_url"]}}
                                )
                        except Exception as pdf_error:
                            logger.warning(f"Failed to generate PDF for batch generation {inserted_id}: {pdf_error}")
        except Exception:
            pass

        # activity log
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "generate_batch",
                    "user": user_summary,
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

# ============ News search endpoints ==========
@app.get("/api/news/search")
async def search_news(
    q: str,
    page_size: int = 4,
    language: str = "en",
    news_service: Any = Depends(get_news_service)
):
    """Search for related real news articles (simple search)"""
    try:
        logger.info(f"News search request: query={q}, page_size={page_size}")
        result = news_service.search_news(
            query=q,
            language=language,
            page_size=page_size
        )
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"News search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class SmartNewsSearchRequest(BaseModel):
    text: str
    detection_result: Optional[Dict] = None
    max_results: Optional[int] = 4
    language: Optional[str] = "en"

@app.post("/api/news/find_related")
async def find_related_news(request: SmartNewsSearchRequest, http_request: Request = None):
    """Smart news search with entity extraction and keyword analysis"""
    try:
        logger.info(f"Smart news search request for text (length: {len(request.text)})")
        
        from services.find_news import related_news_finder
        
        result = related_news_finder.find_related_news(
            text=request.text,
            detection_result=request.detection_result,
            max_results=request.max_results or 4,
            language=request.language or "en"
        )
        
        # Activity log
        try:
            if mongo_service.is_connected():
                mongo_service.insert_one("user_activity_log", {
                    "action": "find_related_news",
                    "user": {},
                    "request_meta": {
                        "text_preview": request.text[:200],
                        "max_results": request.max_results
                    },
                    "result_meta": {
                        "success": result.get('success'),
                        "articles_found": len(result.get('articles', [])),
                        "search_query": result.get('search_query')
                    },
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
        logger.error(f"Smart news search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ============ History query endpoints ==========
class HistoryQuery(BaseModel):
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    q: Optional[str] = None  # text/topic keyword
    image_only: Optional[bool] = False

def _pagination_params(page: Optional[int], page_size: Optional[int]) -> Dict[str, int]:
    p = max(1, int(page or 1))
    ps = max(1, min(int(page_size or 10), 100))
    return {"skip": (p - 1) * ps, "limit": ps}


def _ensure_object_id(value: Any) -> ObjectId:
    """
    Coerce a value to ObjectId, raising HTTPException if invalid.
    """
    if isinstance(value, ObjectId):
        return value
    if isinstance(value, str) and ObjectId.is_valid(value):
        return ObjectId(value)
    raise HTTPException(status_code=400, detail="Invalid user identifier")


def _current_user_object_id(user: Dict[str, Any]) -> ObjectId:
    """
    Resolve the ObjectId for the current user.
    """
    if "_id" in user:
        return _ensure_object_id(user["_id"])
    if "id" in user:
        return _ensure_object_id(user["id"])
    raise HTTPException(status_code=400, detail="User identifier missing")

@app.get("/api/detection/history")
async def get_detection_history(
    page: int = 1,
    page_size: int = 10,
    q: Optional[str] = None,
    image_only: bool = False,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    col = mongo_service.get_collection("detection_results")
    user_object_id = _current_user_object_id(current_user)
    query: Dict[str, Any] = {"user_id": user_object_id}
    if q:
        # Prefer text index; fall back to regex if necessary
        query["$or"] = [
            {"text": {"$regex": q, "$options": "i"}},
            {"type": {"$regex": q, "$options": "i"}}
        ]
    if image_only:
        query["image_url_or_b64"] = {"$ne": None}
    pg = _pagination_params(page, page_size)
    total = col.count_documents(query)
    cursor = col.find(query).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])  # type: ignore
    items = list(cursor)
    # Convert ObjectId to string to keep responses JSON-friendly
    for it in items:
        if it.get("_id") is not None:
            it["_id"] = str(it["_id"])  # type: ignore
        if isinstance(it.get("user_id"), ObjectId):
            it["user_id"] = str(it["user_id"])
    return {"success": True, "total": total, "page": page, "page_size": page_size, "items": items}

@app.delete("/api/detection/history/{record_id}")
async def delete_detection_record(
    record_id: str,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    """
    Delete a specific detection record.
    
    Args:
        record_id: MongoDB ObjectId string of the record
        user_id: Optional user id, used to verify ownership when provided
    
    Returns:
        Deletion result
    """
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    # Validate ObjectId format
    try:
        object_id = ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid record ID format")
    
    col = mongo_service.get_collection("detection_results")
    
    # Build query with ownership check
    user_object_id = _current_user_object_id(current_user)
    query: Dict[str, Any] = {"_id": object_id, "user_id": user_object_id}
    
    # Ensure record exists before deletion
    record = col.find_one(query)
    if not record:
        raise HTTPException(
            status_code=404,
            detail="Record not found or does not belong to the current user"
        )
    
    # Delete record
    try:
        result = col.delete_one({"_id": object_id})
        if result.deleted_count > 0:
            return {
                "success": True,
                "message": "Record deleted successfully",
                "deleted_id": record_id
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete record")
    except Exception as e:
        logger.error(f"Error deleting detection record {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete record: {str(e)}")

@app.get("/api/detection/history/{record_id}/pdf")
async def download_detection_pdf(
    record_id: str,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    """
    Download the detection result PDF.
    
    Args:
        record_id: Detection record ID
    
    Returns:
        PDF file response
    """
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        object_id = ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid record ID format")
    
    col = mongo_service.get_collection("detection_results")
    record = col.find_one({"_id": object_id})
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    user_object_id = _current_user_object_id(current_user)
    record_user_id = record.get("user_id")
    if record_user_id is not None and _ensure_object_id(record_user_id) != user_object_id:
        raise HTTPException(status_code=403, detail="You do not have access to this record")
    
    # Check if PDF exists
    pdf_path = record.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated for this record")
    
    # Convert to absolute path if relative
    pdf_file = Path(pdf_path)
    if not pdf_file.is_absolute():
        # If relative path, resolve from backend directory
        backend_dir = Path(__file__).parent
        pdf_file = backend_dir / pdf_path
    
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found at {pdf_file}")
    
    return FileResponse(
        path=str(pdf_file.absolute()),
        media_type="application/pdf",
        filename=f"detection_{record_id}.pdf"
    )

@app.get("/api/generation/history/{record_id}/pdf")
async def download_generation_pdf(
    record_id: str,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    """
    Download the generation result PDF.
    
    Args:
        record_id: Generation record ID
    
    Returns:
        PDF file response
    """
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        object_id = ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid record ID format")
    
    col = mongo_service.get_collection("generation_results")
    record = col.find_one({"_id": object_id})
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    user_object_id = _current_user_object_id(current_user)
    record_user_id = record.get("user_id")
    if record_user_id is not None and _ensure_object_id(record_user_id) != user_object_id:
        raise HTTPException(status_code=403, detail="You do not have access to this record")
    
    # Check if PDF exists
    pdf_path = record.get("pdf_path")
    if not pdf_path:
        raise HTTPException(status_code=404, detail="PDF not generated for this record")
    
    # Convert to absolute path if relative
    pdf_file = Path(pdf_path)
    if not pdf_file.is_absolute():
        # If relative path, resolve from backend directory
        backend_dir = Path(__file__).parent
        pdf_file = backend_dir / pdf_path
    
    if not pdf_file.exists():
        raise HTTPException(status_code=404, detail=f"PDF file not found at {pdf_file}")
    
    return FileResponse(
        path=str(pdf_file.absolute()),
        media_type="application/pdf",
        filename=f"generation_{record_id}.pdf"
    )

@app.post("/api/detection/history/{record_id}/generate_pdf")
async def generate_detection_pdf_on_demand(
    record_id: str,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    """
    Generate a detection PDF on demand for a specific record.
    
    Args:
        record_id: Detection record ID
    
    Returns:
        Result containing the PDF URL if successful
    """
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        object_id = ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid record ID format")
    
    col = mongo_service.get_collection("detection_results")
    record = col.find_one({"_id": object_id})
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    user_object_id = _current_user_object_id(current_user)
    record_user_id = record.get("user_id")
    if record_user_id is not None and _ensure_object_id(record_user_id) != user_object_id:
        raise HTTPException(status_code=403, detail="You do not have access to this record")
    
    # Generate PDF
    try:
        detection_data = dict(record)
        detection_data.pop("_id", None)
        # Convert ObjectId to string for PDF filename
        pdf_info = pdf_service.generate_detection_pdf(str(record["_id"]), detection_data)
        
        if pdf_info:
            # Update record with PDF paths
            col.update_one(
                {"_id": object_id},
                {"$set": {"pdf_path": pdf_info["pdf_path"], "pdf_url": pdf_info["pdf_url"]}}
            )
            return {
                "success": True,
                "message": "PDF generated successfully",
                "pdf_url": pdf_info["pdf_url"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
    except Exception as e:
        logger.error(f"Error generating PDF for detection {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.post("/api/generation/history/{record_id}/generate_pdf")
async def generate_generation_pdf_on_demand(
    record_id: str,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    """
    Generate a generation result PDF on demand.
    
    Args:
        record_id: Generation record ID
    
    Returns:
        Result containing the PDF URL if successful
    """
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    
    try:
        object_id = ObjectId(record_id)
    except (InvalidId, Exception):
        raise HTTPException(status_code=400, detail="Invalid record ID format")
    
    col = mongo_service.get_collection("generation_results")
    record = col.find_one({"_id": object_id})
    
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    user_object_id = _current_user_object_id(current_user)
    record_user_id = record.get("user_id")
    if record_user_id is not None and _ensure_object_id(record_user_id) != user_object_id:
        raise HTTPException(status_code=403, detail="You do not have access to this record")
    
    # Generate PDF
    try:
        generation_data = dict(record)
        generation_data.pop("_id", None)
        # Convert ObjectId to string for PDF filename
        pdf_info = pdf_service.generate_generation_pdf(str(record["_id"]), generation_data)
        
        if pdf_info:
            # Update record with PDF paths
            col.update_one(
                {"_id": object_id},
                {"$set": {"pdf_path": pdf_info["pdf_path"], "pdf_url": pdf_info["pdf_url"]}}
            )
            return {
                "success": True,
                "message": "PDF generated successfully",
                "pdf_url": pdf_info["pdf_url"]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
    except Exception as e:
        logger.error(f"Error generating PDF for generation {record_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@app.get("/api/generation/history")
async def get_generation_history(
    page: int = 1,
    page_size: int = 10,
    q: Optional[str] = None,
    image_only: bool = False,
    current_user: Dict[str, Any] = Depends(require_active_user)
):
    if not mongo_service.is_connected():
        raise HTTPException(status_code=503, detail="Database not connected")
    col = mongo_service.get_collection("generation_results")
    user_object_id = _current_user_object_id(current_user)
    query: Dict[str, Any] = {"user_id": user_object_id}
    if q:
        query["$or"] = [
            {"topic": {"$regex": q, "$options": "i"}},
            {"strategy": {"$regex": q, "$options": "i"}},
        ]
    if image_only:
        query["image_url_or_b64"] = {"$ne": None}
    pg = _pagination_params(page, page_size)
    total = col.count_documents(query)
    cursor = col.find(query).sort("created_at", -1).skip(pg["skip"]).limit(pg["limit"])  # type: ignore
    items = list(cursor)
    for it in items:
        if it.get("_id") is not None:
            it["_id"] = str(it["_id"])  # type: ignore
        if isinstance(it.get("user_id"), ObjectId):
            it["user_id"] = str(it["user_id"])
    return {"success": True, "total": total, "page": page, "page_size": page_size, "items": items}

# Legacy endpoints (for backward compatibility)
@app.post("/generate_text")
async def generate_text_legacy(
    request: GenerationRequest,
    service: Any = Depends(get_generation_service),
    news_service: Any = Depends(get_news_service),
    vision: Any = Depends(get_vision_service),
    current_user: Dict[str, Any] = Depends(require_active_user),
    http_request: Request = None
):
    """Legacy generation endpoint"""
    return await generate_single(
        request=request,
        service=service,
        news_service=news_service,
        vision=vision,
        current_user=current_user,
        http_request=http_request,
    )

@app.post("/detect_text")
async def detect_text_legacy(
    request: DetectionRequest,
    service: Any = Depends(get_detection_service),
    vision: Any = Depends(get_vision_service),
    current_user: Dict[str, Any] = Depends(require_active_user),
    http_request: Request = None
):
    """Legacy text detection endpoint"""
    return await baseline_detection(
        request=request,
        service=service,
        vision=vision,
        current_user=current_user,
        http_request=http_request,
    )

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
