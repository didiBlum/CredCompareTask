from fastapi import FastAPI
import asyncio
from app.api.routes import router
from app.services.source_service import load_sources_from_config
from app.db import ensure_indexes
import logging
import os
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger("main")

PERIODIC_FETCH_INTERVAL_SECONDS = 600  # 10 minutes

app = FastAPI()
app.include_router(router)


async def periodic_fetch_for_source(source):
    while True:
        logger.info(f"[Periodic Fetch] Fetching source: {source.name}")
        await source.fetch_and_save()
        await asyncio.sleep(source.cadence_seconds)

@app.on_event("startup")
async def startup():
    await ensure_indexes()
    sources = load_sources_from_config()
    for source in sources:
        if source.enabled:
            asyncio.create_task(periodic_fetch_for_source(source)) 