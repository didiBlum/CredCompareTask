from app.services.shared_db import save_item_to_db, log_event_to_db
from app.models.log_event import LogEvent
from datetime import datetime, timezone
from fastapi import HTTPException
from app.models.item import Item
from sources import SOURCE_HANDLERS

async def handle_webhook_data(data: dict, source: str):
    try:
        data = dict(data)
        handler = SOURCE_HANDLERS.get(source)
        items = []
        if handler:
            result = handler(data)
            if isinstance(result, list):
                items = result
            else:
                items = [result]
        else:
            # Fallback: treat as single item
            data["source_name"] = source
            items = [Item(**data)]
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
        await log_event_to_db(LogEvent(
            source_name=source,
            time=datetime.now(timezone.utc),
            items_saved=0,
            error=f"{type(e).__name__}: {e}",
            type="webhook"
        ))
        raise HTTPException(status_code=400, detail=f"Webhook error: {e}") 