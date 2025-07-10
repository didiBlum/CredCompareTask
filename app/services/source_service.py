import httpx
import asyncio
import json
from pathlib import Path
from app.services.shared_db import save_item_to_db, log_event_to_db
from app.models.item import Item
import logging
import traceback
from app.models.log_event import LogEvent
from datetime import datetime, timezone
from app.utils import convert_object_ids_to_str
logger = logging.getLogger("source_service")

DEFAULT_TIMEOUT = 30
CONFIG_PATH = Path("sources_config.json")

class DataSource:
    def __init__(self, name, url, parser=None):
        self.name = name
        self.url = url
        self.parser = parser  # Custom parser function

    def parse(self, data) -> Item:
        if self.parser:
            return self.parser(data)
        # Default: map data to Item, set source_name
        return Item(
            title=data.get("title", str(data)),
            content=data.get("content", str(data)),
            source_name=self.name,
            topic_name=data.get("topic_name", data.get("topic", "")),
            created_at=data.get("created_at") or __import__('datetime').datetime.now(__import__('datetime').timezone.utc)
        )

    async def fetch_items(self) -> list[Item]:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            resp = await client.get(self.url)
            resp.raise_for_status()
            data = resp.json()
            logger.debug(f"[Fetch] Raw data received from {self.name}: {data}")
            if isinstance(data, list):
                return [self.parse(item) for item in data]
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
            return {"source": self.name, "error": error_details}

def load_sources_from_config():
    if not CONFIG_PATH.exists():
        return []
    with open(CONFIG_PATH) as f:
        config = json.load(f)
    sources = [DataSource(src["name"], src["url"]) for src in config.get("sources", [])]
    return sources

async def fetch_all_sources():
    sources = load_sources_from_config()
    results = await asyncio.gather(*(source.fetch_and_save() for source in sources))
    return results 