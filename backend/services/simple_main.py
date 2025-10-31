"""
Simplified main server for fake news detection system
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime
from simple_detection import SimpleDetectionService
from services.generation_service import GenerationService
from services.news_service import NewsService
from config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI application
app = FastAPI(
    title="Simple Fake News Detection System",
    description="Simplified fake news detection and generation system",
    version="1.0.0"
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
simple_detection_service = None
generation_service = None
news_service = None

# Pydantic models
class DetectionRequest(BaseModel):
    text: str

class GenerationRequest(BaseModel):
    topic: str
    strategy: Optional[str] = "loaded_language"
    model_type: Optional[str] = "gpt-4o"
    style: Optional[str] = None  # formal | sensational | fun | normal
    domain: Optional[str] = None  # politics | business | sports | technology

class NewsRequest(BaseModel):
    query: Optional[str] = None
    country: Optional[str] = "us"
    category: Optional[str] = None
    page_size: Optional[int] = 10

class RealBasedGenerationRequest(BaseModel):
    source_text: str
    source_url: Optional[str] = None
    label: Optional[str] = None  # Supported | Refuted | NotEnoughInfo (if from dataset)
    topic: Optional[str] = None
    strategy: Optional[str] = "loaded_language"
    model_type: Optional[str] = "gpt-4o"
    style: Optional[str] = None  # formal | sensational | fun | normal
    domain: Optional[str] = None  # politics | business | sports | technology

class DatasetItemRequest(BaseModel):
    id: Optional[str] = None
    source_text: str
    source_url: Optional[str] = None
    label: Optional[str] = None
    topic: Optional[str] = None
    strategy: Optional[str] = "loaded_language"
    model_type: Optional[str] = "gpt-4o"
    style: Optional[str] = None
    domain: Optional[str] = None
    use_full_content: Optional[bool] = False

class DatasetBatchRequest(BaseModel):
    items: list[DatasetItemRequest]

class QueryGenRequest(BaseModel):
    query: str
    label: Optional[str] = None
    strategy: Optional[str] = "loaded_language"
    model_type: Optional[str] = "gpt-4o"
    style: Optional[str] = None
    domain: Optional[str] = None
    use_full_content: Optional[bool] = False
    language: Optional[str] = "en"  # forwarded to NewsAPI
    sources_whitelist: Optional[list[str]] = None  # list of allowed domains

class QueryBatchRequest(BaseModel):
    query: str
    size: Optional[int] = 5
    label: Optional[str] = None
    strategy: Optional[str] = "loaded_language"
    model_type: Optional[str] = "gpt-4o"
    style: Optional[str] = None
    domain: Optional[str] = None
    use_full_content: Optional[bool] = False
    language: Optional[str] = "en"
    sources_whitelist: Optional[list[str]] = None

# Dependency injection
def get_simple_detection_service():
    global simple_detection_service
    if simple_detection_service is None:
        simple_detection_service = SimpleDetectionService()
    return simple_detection_service

def get_generation_service():
    global generation_service
    if generation_service is None:
        generation_service = GenerationService()
    return generation_service

def get_news_service():
    global news_service
    if news_service is None:
        news_service = NewsService()
    return news_service

# API routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Simple Fake News Detection System",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "detection": simple_detection_service is not None,
            "generation": generation_service is not None,
            "news": news_service is not None
        }
    }

@app.post("/api/detect/simple")
async def simple_detection_endpoint(
    request: DetectionRequest,
    service: SimpleDetectionService = Depends(get_simple_detection_service)
):
    """Simple detection using GPT-4o"""
    try:
        logger.info(f"Simple detection request for text: {request.text[:100]}...")
        
        result = service.detect_fake_news(request.text)
        
        return {
            "success": True,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Simple detection error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/single")
async def generate_single(
    request: GenerationRequest,
    service: GenerationService = Depends(get_generation_service)
):
    """Back-compat: interpret topic as query, fetch a real article, then generate.

    This preserves the "enter prompt -> generate" UX by chaining to the NewsAPI search
    and our from_real generator. The final article always ends with the real URL.
    """
    try:
        # Use topic as a news query
        query = request.topic
        if not query:
            raise HTTPException(status_code=400, detail="topic (query) is required")

        # Lazy import to avoid circulars
        n_service = get_news_service()
        news = n_service.search_news(query=query, language="en", page_size=1)
        articles = (news or {}).get("articles") or []
        if not articles:
            raise HTTPException(status_code=404, detail="No news articles found for the given topic")

        a0 = articles[0]
        title = a0.get("title") or ""
        desc = a0.get("description") or ""
        url = a0.get("url") or ""
        if not url:
            raise HTTPException(status_code=502, detail="News article missing URL")

        # Try to fetch full content for better grounding
        source_text = (title + "\n\n" + desc).strip()
        try:
            import urllib.request, re, html
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
            fetched_text = "\n\n".join(cleaned)
            if fetched_text:
                source_text = fetched_text
        except Exception:
            pass

        result = service.generate_from_real({
            "source_text": source_text,
            "source_url": url,
            "label": None,
            "strategy": request.strategy,
            "model_type": request.model_type,
            "style": request.style,
            "domain": request.domain,
        })

        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/from_real")
async def generate_from_real(
    request: RealBasedGenerationRequest,
    service: GenerationService = Depends(get_generation_service)
):
    """Generate fake news based on a real article (manipulation)."""
    try:
        logger.info("Generation-from-real request received")
        result = service.generate_from_real(request.dict())
        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Generation-from-real error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/from_dataset_item")
async def generate_from_dataset_item(
    request: DatasetItemRequest,
    service: GenerationService = Depends(get_generation_service)
):
    """Generate fake news for a single dataset item (RAW-style)."""
    try:
        payload = {
            "source_text": request.source_text,
            "source_url": request.source_url,
            "label": request.label,
            "topic": request.topic,
            "strategy": request.strategy,
            "model_type": request.model_type,
            "style": request.style,
            "domain": request.domain,
        }
        # Enforce presence of source_url
        if not request.source_url:
            raise HTTPException(status_code=400, detail="source_url is required for dataset-based generation")
        # Optionally fetch full content
        if request.use_full_content and request.source_url:
            try:
                import urllib.request, re, html
                req = urllib.request.Request(request.source_url, headers={"User-Agent": "Mozilla/5.0"})
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
                fetched_text = "\n\n".join(cleaned)
                if fetched_text:
                    payload["source_text"] = fetched_text
            except Exception:
                pass
        result = service.generate_from_real(payload)
        if request.id:
            result["dataset_id"] = request.id
        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Dataset item generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/from_dataset_batch")
async def generate_from_dataset_batch(
    request: DatasetBatchRequest,
    service: GenerationService = Depends(get_generation_service)
):
    """Batch generate fake news for a list of dataset items."""
    try:
        outputs = []
        for item in request.items:
            payload = {
                "source_text": item.source_text,
                "source_url": item.source_url,
                "label": item.label,
                "topic": item.topic,
                "strategy": item.strategy,
                "model_type": item.model_type,
                "style": item.style,
                "domain": item.domain,
            }
            if not item.source_url:
                outputs.append({"success": False, "error": "source_url is required", "dataset_id": item.id})
                continue
            if item.use_full_content and item.source_url:
                try:
                    import urllib.request, re, html
                    req = urllib.request.Request(item.source_url, headers={"User-Agent": "Mozilla/5.0"})
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
                    fetched_text = "\n\n".join(cleaned)
                    if fetched_text:
                        payload["source_text"] = fetched_text
                except Exception:
                    pass
            res = service.generate_from_real(payload)
            if item.id:
                res["dataset_id"] = item.id
            outputs.append(res)
        return {
            "success": True,
            "results": outputs,
            "count": len(outputs),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Dataset batch generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/from_query")
async def generate_from_query(
    request: QueryGenRequest,
    g_service: GenerationService = Depends(get_generation_service),
    n_service: NewsService = Depends(get_news_service)
):
    """Search real news by query, then generate manipulated article with original URL appended."""
    try:
        # 1) search news
        lang = (request.language or "en")
        news = n_service.search_news(query=request.query, language=lang, page_size=5)
        articles = (news or {}).get("articles") or []
        if not articles:
            raise HTTPException(status_code=404, detail="No news articles found for the given query")
        # Filter by whitelist if provided
        wl = request.sources_whitelist or [
            "apnews.com", "reuters.com", "bbc.com", "theguardian.com",
            "bloomberg.com", "nytimes.com", "washingtonpost.com"
        ]
        def allowed(u: str) -> bool:
            try:
                from urllib.parse import urlparse
                host = (urlparse(u).netloc or "").lower()
                return any(host.endswith(d) for d in wl)
            except Exception:
                return False
        a0 = next((a for a in articles if a.get("url") and allowed(a.get("url"))), None)
        if not a0:
            # Fallback to first available article if whitelist yields none
            a0 = articles[0]
        title = a0.get("title") or ""
        desc = a0.get("description") or ""
        url = a0.get("url") or ""
        if not url:
            raise HTTPException(status_code=502, detail="News article missing URL")

        # Optional: fetch full content
        fetched_text = ""
        if request.use_full_content:
            try:
                import urllib.request, re, html
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    raw = resp.read()
                text = raw.decode("utf-8", errors="ignore")
                # Remove scripts/styles
                text = re.sub(r"<script[\s\S]*?</script>", " ", text, flags=re.IGNORECASE)
                text = re.sub(r"<style[\s\S]*?</style>", " ", text, flags=re.IGNORECASE)
                # Prefer <article> content
                article_match = re.search(r"<article[\s\S]*?</article>", text, flags=re.IGNORECASE)
                candidate = article_match.group(0) if article_match else text
                # Join <p> blocks
                paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", candidate, flags=re.IGNORECASE)
                cleaned = []
                for p in paragraphs[:20]:
                    # strip tags
                    p_txt = re.sub(r"<[^>]+>", " ", p)
                    p_txt = html.unescape(p_txt)
                    p_txt = re.sub(r"\s+", " ", p_txt).strip()
                    if p_txt:
                        cleaned.append(p_txt)
                fetched_text = "\n\n".join(cleaned)
            except Exception as _:
                fetched_text = ""

        # 2) compose source_text fallback
        source_text = fetched_text.strip() if fetched_text else (title + "\n\n" + desc).strip() if title or desc else title or desc or ""
        if not source_text:
            source_text = title or desc or "News summary unavailable."

        # 3) call generation
        payload = {
            "source_text": source_text,
            "source_url": url,
            "label": request.label,
            "strategy": request.strategy,
            "model_type": request.model_type,
            "style": request.style,
            "domain": request.domain,
        }
        result = g_service.generate_from_real(payload)
        return {
            "success": result.get("success", False),
            "result": result,
            "source": {"title": title, "url": url, "used_full_content": bool(fetched_text)},
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query chain generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/from_query_batch")
async def generate_from_query_batch(
    request: QueryBatchRequest,
    g_service: GenerationService = Depends(get_generation_service),
    n_service: NewsService = Depends(get_news_service)
):
    """Batch: search real news by query, take N results, optionally fetch full content, then generate manipulated articles."""
    try:
        page_size = max(1, min(int(request.size or 5), 20))
        lang = (request.language or "en")
        news = n_service.search_news(query=request.query, language=lang, page_size=page_size * 2)
        articles = (news or {}).get("articles") or []
        if not articles:
            raise HTTPException(status_code=404, detail="No news articles found for the given query")
        wl = request.sources_whitelist or [
            "apnews.com", "reuters.com", "bbc.com", "theguardian.com",
            "bloomberg.com", "nytimes.com", "washingtonpost.com"
        ]
        def allowed(u: str) -> bool:
            try:
                from urllib.parse import urlparse
                host = (urlparse(u).netloc or "").lower()
                return any(host.endswith(d) for d in wl)
            except Exception:
                return False
        # keep only allowed and truncate
        filtered = [a for a in articles if a.get("url") and allowed(a.get("url"))]
        articles = (filtered or articles)[:page_size]

        results = []
        for idx, a in enumerate(articles):
            title = a.get("title") or ""
            desc = a.get("description") or ""
            url = a.get("url") or ""
            if not url:
                results.append({"success": False, "error": "missing URL", "index": idx})
                continue

            fetched_text = ""
            if request.use_full_content:
                try:
                    import urllib.request, re, html
                    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
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
                    fetched_text = "\n\n".join(cleaned)
                except Exception:
                    fetched_text = ""

            source_text = fetched_text.strip() if fetched_text else (title + "\n\n" + desc).strip() if title or desc else title or desc or ""
            if not source_text:
                source_text = title or desc or "News summary unavailable."

            payload = {
                "source_text": source_text,
                "source_url": url,
                "label": request.label,
                "strategy": request.strategy,
                "model_type": request.model_type,
                "style": request.style,
                "domain": request.domain,
            }
            res = g_service.generate_from_real(payload)
            res["source"] = {"title": title, "url": url, "used_full_content": bool(fetched_text)}
            results.append(res)

        return {
            "success": True,
            "results": results,
            "count": len(results),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query batch generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/headlines")
async def get_headlines(
    country: str = "us",
    category: Optional[str] = None,
    page_size: int = 10,
    service: NewsService = Depends(get_news_service)
):
    """Get top headlines from News API"""
    try:
        logger.info(f"Headlines request: country={country}, category={category}")
        
        result = service.get_top_headlines(
            country=country,
            category=category,
            page_size=page_size
        )
        
        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Headlines error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/search")
async def search_news(
    query: str,
    language: str = "en",
    page_size: int = 10,
    service: NewsService = Depends(get_news_service)
):
    """Search for news articles"""
    try:
        logger.info(f"News search request: query={query}")
        
        result = service.search_news(
            query=query,
            language=language,
            page_size=page_size
        )
        
        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"News search error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news/sources")
async def get_sources(
    category: Optional[str] = None,
    language: str = "en",
    country: str = "us",
    service: NewsService = Depends(get_news_service)
):
    """Get available news sources"""
    try:
        logger.info(f"Sources request: category={category}")
        
        result = service.get_sources(
            category=category,
            language=language,
            country=country
        )
        
        return {
            "success": result.get("success", False),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Sources error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    
    # Create logs directory
    import os
    os.makedirs("logs", exist_ok=True)
    
    # Start service
    uvicorn.run(
        "simple_main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
