from app.db import collection, db
from bson import ObjectId
from datetime import datetime, timezone
from app.utils import convert_object_ids_to_str
from app.models.item import Item
from app.models.log_event import LogEvent

log_collection = db["log_events"]

async def save_item_to_db(item: Item):
    item_doc = item.dict(by_alias=True, exclude_unset=True)
    # Lookup or create source by name
    source_name = item_doc.get("source_name")
    if source_name:
        source = await db["sources"].find_one({"name": source_name})
        if not source:
            await db["sources"].insert_one({"name": source_name})
        item_doc["source_name"] = source_name
    # Set created_at and updated_at to current UTC time
    now = datetime.now(timezone.utc).isoformat()
    item_doc["created_at"] = now
    item_doc["updated_at"] = now
    result = await collection.insert_one(item_doc)
    item_doc["_id"] = result.inserted_id
    return convert_object_ids_to_str(item_doc)

async def log_event_to_db(event: LogEvent):
    event_doc = event.dict(by_alias=True, exclude_unset=True)
    result = await log_collection.insert_one(event_doc)
    event_doc["_id"] = result.inserted_id
    return event_doc 