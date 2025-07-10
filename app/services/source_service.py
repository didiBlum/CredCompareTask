import httpx
import asyncio
import json
from pathlib import Path
from app.services.shared_db import save_item_to_db, log_event_to_db
from app.models.item import Item
import logging
import traceback
from app.models.log_event import LogEvent
from sources import get_handler_by_name, get_error_handler_by_name
from datetime import datetime, timezone
from app.utils import convert_object_ids_to_str
import ast
logger = logging.getLogger("source_service")

DEFAULT_TIMEOUT = 30
CONFIG_PATH = Path("sources_config.json")

class DataSource:
    def __init__(self, name, url, handler=None, auth=None, cadence_seconds=600, enabled=True, max_items=20, headers=None, error_handler=None):
        self.name = name
        self.url = url
        self.handler = handler
        self.auth = auth or {}
        self.cadence_seconds = cadence_seconds
        self.enabled = enabled
        self.max_items = max_items
        self.headers = headers or {}
        self.error_handler = error_handler

    def parse(self, data) -> Item:
        if self.handler:
            return self.handler(data)
        # Default: map data to Item, set source_name
        return Item(
            title=data.get("title", str(data)),
            content=data.get("content", str(data)),
            source_name=self.name,
            topic_name=data.get("topic_name", data.get("topic", "")),
            created_at=data.get("created_at") or __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        )

    async def fetch_items(self) -> list[Item]:
        headers = dict(self.headers)
        # Auth support
        if self.auth:
            if self.auth.get("type") == "bearer":
                headers["Authorization"] = f"Bearer {self.auth['token']}"
            elif self.auth.get("type") == "basic":
                import base64
                user = self.auth.get("username", "")
                pwd = self.auth.get("password", "")
                headers["Authorization"] = "Basic " + base64.b64encode(f"{user}:{pwd}".encode()).decode()
            elif self.auth.get("type") == "api_key":
                headers[self.auth.get("header", "X-API-Key")] = self.auth["key"]
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(self.url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            logger.debug(f"[Fetch] Raw data received from {self.name}: {data}")
            if isinstance(data, list):
                return [self.parse(item) for item in data][:self.max_items]
            elif isinstance(data, dict):
                return [self.parse(data)]
            else:
                logger.warning(f"[Fetch] Unexpected data format from {self.name}: {data}")
                return []

    async def fetch_and_save(self):
        try:
            items = await self.fetch_items()
            # Save all items in parallel
            results = await asyncio.gather(*(save_item_to_db(item) for item in items))
            logger.info(f"[Save] Items saved from {self.name}: {results}")
            # Log the fetch event
            await log_event_to_db(LogEvent(
                source_name=self.name,
                time=datetime.now(timezone.utc),
                items_saved=len(results),
                type="fetch"
            ))
            return {"source": self.name, "items": [convert_object_ids_to_str(r) for r in results]}
        except Exception as e:
            error_details = f"{type(e).__name__}: {e}"
            if isinstance(e, httpx.HTTPStatusError):
                try:
                    error_body = e.response.text
                    error_details += f" | Response body: {error_body}"
                except Exception as inner:
                    error_details += f" | (Failed to get response body: {inner})"
            logger.error(f"[Error] Fetch or save failed for {self.name}: {error_details}")
            logger.debug(traceback.format_exc())
            # Log the error event
            await log_event_to_db(LogEvent(
                source_name=self.name,
                time=datetime.now(timezone.utc),
                items_saved=0,
                error=error_details,
                type="fetch"
            ))
            # Call custom error handler if provided
            if self.error_handler:
                return self.error_handler(self, e, error_details)
            else:
                return default_error_handler(self, e, error_details)

def load_sources_from_config():
    if not CONFIG_PATH.exists():
        return []
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    sources = []
    for src in config.get("sources", []):
        handler = None
        if "handler" in src:
            handler = get_handler_by_name(src["handler"])
        elif "name" in src:
            handler = get_handler_by_name(src["name"])
        error_handler = None
        if "error_handler" in src:
            error_handler = get_error_handler_by_name(src["error_handler"])
        sources.append(DataSource(
            name=src["name"],
            url=src["url"],
            handler=handler,
            auth=src.get("auth"),
            cadence_seconds=src.get("cadence_seconds", 600),
            enabled=src.get("enabled", True),
            max_items=src.get("max_items", 20),
            headers=src.get("headers", {})
            ,error_handler=error_handler
        ))
    return sources

# Default error handler
def default_error_handler(source, exc, error_details):
    logger.error(f"[Default Error Handler] Source: {source.name}, Error: {error_details}")
    return {"source": source.name, "error": error_details}

async def fetch_all_sources():
    sources = load_sources_from_config()
    results = await asyncio.gather(*(source.fetch_and_save() for source in sources))
    return results 