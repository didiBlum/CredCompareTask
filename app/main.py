from fastapi import FastAPI
import asyncio
from app.api.routes import router
from app.services.source_service import fetch_all_sources
from app.db import ensure_indexes
import logging
import os
logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
logger = logging.getLogger("main")

PERIODIC_FETCH_INTERVAL_SECONDS = 600  # 10 minutes

app = FastAPI()
app.include_router(router)

async def periodic_fetch():
    while True:
        logger.info("[Periodic Fetch] Fetching all sources...")
        await fetch_all_sources()
        await asyncio.sleep(PERIODIC_FETCH_INTERVAL_SECONDS)

@app.on_event("startup")
async def startup():
    await ensure_indexes()
    asyncio.create_task(periodic_fetch()) 