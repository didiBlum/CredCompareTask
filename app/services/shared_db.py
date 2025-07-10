from app.db import collection, db
from bson import ObjectId
from datetime import datetime, timezone
from app.services.utils import to_str_id
from app.models.item import Item

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
    return to_str_id(item_doc) 