from app.services.shared_db import save_item_to_db, log_event_to_db
from app.models.log_event import LogEvent
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.item import Item

async def handle_webhook_data(data: dict, source: str):
    try:
        data = dict(data)
        data["source_name"] = source
        item = Item(**data)
        saved = await save_item_to_db(item)
        await log_event_to_db(LogEvent(
            source_name=source,
            time=datetime.now(timezone.utc),
            items_saved=1,
            type="webhook"
        ))
        return saved
    except Exception as e:
        await log_event_to_db(LogEvent(
            source_name=source,
            time=datetime.now(timezone.utc),
            items_saved=0,
            error=f"{type(e).__name__}: {e}",
            type="webhook"
        ))
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}") 