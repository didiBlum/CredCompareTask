from app.services.shared_db import save_item_to_db, log_event_to_db
from app.models.log_event import LogEvent
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.item import Item
from sources import get_handler_by_name
import logging
import traceback
logger = logging.getLogger("webhook_service")

async def default_webhook_handler(request, source):
    data = await request.json()
    # Fill required fields with defaults if missing
    for field in ["title", "content", "topic_name"]:
        if not data.get(field):
            logger.warning(f"[Default Handler] Missing '{field}' in webhook data for source {source}, using default 'unknown'. Data: {data}")
            data[field] = "unknown"
    if not data.get("source_name"):
        data["source_name"] = source
    if not data.get("created_at"):
        data["created_at"] = datetime.now(timezone.utc)
    return Item(**data)

async def handle_webhook_data(request, source: str):
    try:
        handler = get_handler_by_name(source)
        if not handler:
            handler = lambda req: default_webhook_handler(req, source)
        result = await handler(request)
        # If the handler returns a dict, coerce to Item with defaults and log warning
        if isinstance(result, dict):
            item_dict = dict(result)
            for field in ["title", "content", "topic_name"]:
                if not item_dict.get(field):
                    logger.warning(f"Missing '{field}' in webhook data for source {source}, using default 'unknown'. Data: {item_dict}")
                    item_dict[field] = "unknown"
            if not item_dict.get("source_name"):
                item_dict["source_name"] = source
            if not item_dict.get("created_at"):
                item_dict["created_at"] = datetime.now(timezone.utc)
            items = [Item(**item_dict)]
        elif isinstance(result, list):
            items = result
        else:
            items = [result]
        saved = []
        for item in items:
            saved.append(await save_item_to_db(item))
        await log_event_to_db(LogEvent(
            source_name=source,
            time=datetime.now(timezone.utc),
            items_saved=len(saved),
            type="webhook"
        ))
        return saved if len(saved) > 1 else saved[0]
    except Exception as e:
        logger.error(f"[Webhook Error] Source: {source}, Exception: {type(e).__name__}: {e}\n{traceback.format_exc()}")
        await log_event_to_db(LogEvent(
            source_name=source,
            time=datetime.now(timezone.utc),
            items_saved=0,
            error=f"{type(e).__name__}: {e}",
            type="webhook"
        ))
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}") 