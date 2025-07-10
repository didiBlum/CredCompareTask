from fastapi import FastAPI
import asyncio
from app.api.routes import router
from app.services.source_service import load_sources_from_config
from app.db import ensure_indexes
import logging
import os
import httpx
import asyncio
import random
from datetime import datetime
import hmac
import hashlib
import json
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

async def fake_webhook_trigger():
    await asyncio.sleep(10)
    host = os.environ.get("WEBHOOK_HOST", "http://127.0.0.1:8000")
    url = f"{host}/webhook?source=test"
    content = f"Random content {random.randint(1, 10000)}"
    payload = {
        "title": "Triggered item",
        "content": content,
        "timestamp": datetime.utcnow().isoformat(),
        "topic": "interviews"
    }
    # Simple static secret header
    secret = "testsecret"
    body = json.dumps(payload, separators=(",", ":")).encode()
    headers = {"X-Test-Webhook-Secret": secret, "Content-Type": "application/json"}
    try:
        resp = await httpx.post(url, data=body, headers=headers)
        print(f"Fake webhook sent, status: {resp.status_code}, response: {resp.text}")
    except Exception as e:
        print(f"Fake webhook failed: {e}")
    # Set WEBHOOK_HOST to your deployed URL, e.g. https://your-app.herokuapp.com

@app.on_event("startup")
async def startup():
    await ensure_indexes()
    sources = load_sources_from_config()
    for source in sources:
        if source.enabled:
            asyncio.create_task(periodic_fetch_for_source(source))
    # Start the fake webhook trigger as a background task
    asyncio.create_task(fake_webhook_trigger()) 