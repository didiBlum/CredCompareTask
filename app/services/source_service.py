import httpx
import asyncio
import json
from pathlib import Path
from app.services.shared_db import save_item_to_db
from app.services.utils import to_str_id
import traceback
from app.models.item import Item

DEFAULT_TIMEOUT = 5  # seconds
CONFIG_PATH = Path("sources_config.json")

class DataSource:
    def __init__(self, name, url, parser=None):
        self.name = name
        self.url = url
        self.parser = parser  # Optional custom parser function

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
            if isinstance(data, list):
                return [self.parse(item) for item in data]
            elif isinstance(data, dict):
                return [self.parse(data)]
            else:
                return []

    async def fetch_and_save(self):
        try:
            items = await self.fetch_items()
            # Save all items in parallel
            results = await asyncio.gather(*(save_item_to_db(item) for item in items))
            print(f"[Save] Items saved from {self.name}: {results}")
            return {"source": self.name, "items": [to_str_id(r) for r in results]}
        except Exception as e:
            print(f"[Error] Fetch or save failed for {self.name}: {type(e).__name__}: {e}")
            traceback.print_exc()
            return {"source": self.name, "error": f"{type(e).__name__}: {e}"}

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