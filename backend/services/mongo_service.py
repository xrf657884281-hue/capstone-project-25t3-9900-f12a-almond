"""
MongoDB service for MCP Fake News Detection System
"""
from typing import Any, Dict, Optional
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from datetime import datetime

from config import Config


class MongoService:
    """Thin wrapper around PyMongo with basic helpers."""

    def __init__(self, url: Optional[str] = None, database: Optional[str] = None):
        base_url = url or Config.MONGODB_URL
        
        if 'authSource=' not in base_url:
            if '?' in base_url:
                base_url = base_url + '&authSource=admin'
            else:
                base_url = base_url + '?authSource=admin'
        self.url = base_url
        self.database_name = database or Config.MONGODB_DATABASE
        self.client: Optional[MongoClient] = None
        self.db = None
        self._connect()

    def _connect(self) -> None:
        try:
            self.client = MongoClient(self.url, serverSelectionTimeoutMS=3000)
            # trigger server selection
            self.client.admin.command("ping")
            self.db = self.client[self.database_name]
        except Exception:
            self.client = None
            self.db = None

    def is_connected(self) -> bool:
        return self.client is not None and self.db is not None

    def get_collection(self, name: str):
        if self.db is None:
            raise RuntimeError("MongoService not connected")
        return self.db[name]

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Optional[str]:
        """Insert a single document and return inserted id as string."""
        try:
            col = self.get_collection(collection)
            # Some collections may have strict validators from seed scripts.
            # Use bypass_document_validation so logging collections (e.g. user_activity_log)
            # are not blocked by required fields.
            res = col.insert_one(document, bypass_document_validation=True)
            return str(res.inserted_id)
        except Exception:
            return None

    def ensure_indexes(self) -> None:
        """Create basic indexes for frequently queried collections."""
        if not self.is_connected():
            self._connect()
        if not self.is_connected():
            return
        try:
            # user_activity_log indexes
            try:
                self.db["user_activity_log"].create_index([("created_at", -1)])
            except Exception:
                pass
            try:
                self.db["user_activity_log"].create_index([("action", 1)])
            except Exception:
                pass
            # users unique indexes
            try:
                self.db["users"].create_index([("username", 1)], unique=True)
            except Exception:
                pass
            try:
                self.db["users"].create_index([("email", 1)], unique=True)
            except Exception:
                pass
            self.db["detection_results"].create_index([("created_at", -1)])
            self.db["detection_results"].create_index([("type", 1)])
            self.db["detection_results"].create_index([("user_id", 1), ("created_at", -1)])
            self.db["generation_results"].create_index([("created_at", -1)])
            self.db["generation_results"].create_index([("topic", 1)])
            self.db["generation_results"].create_index([("user_id", 1), ("created_at", -1)])
        except Exception:
            pass

    def health(self) -> Dict[str, Any]:
        try:
            if not self.is_connected():
                self._connect()
            info: Dict[str, Any] = {"connected": self.is_connected()}
            if self.is_connected():
                info.update({
                    "database": self.database_name,
                    "collections": sorted(self.db.list_collection_names()),
                    "counts": {
                        "users": self.db["users"].count_documents({}) if "users" in self.db.list_collection_names() else 0,
                        "news_articles": self.db["news_articles"].count_documents({}) if "news_articles" in self.db.list_collection_names() else 0,
                    },
                })
            return {"ok": True, "info": info, "timestamp": datetime.utcnow().isoformat()}
        except PyMongoError as e:
            return {"ok": False, "error": str(e), "timestamp": datetime.utcnow().isoformat()}


# singleton for app-wide reuse
mongo_service = MongoService()


