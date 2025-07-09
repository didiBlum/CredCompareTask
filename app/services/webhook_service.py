from app.db import collection, db
from bson import ObjectId
from datetime import datetime, timezone

def to_str_id(doc):
    doc = dict(doc)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

async def handle_webhook_data(data: dict):
    # Store all fields from the incoming data
    item_doc = dict(data)
    # Ensure common fields are present and mapped
    if "title" not in item_doc and "data" in item_doc:
        item_doc["title"] = item_doc["data"]
    if "content" not in item_doc and "data" in item_doc:
        item_doc["content"] = item_doc["data"]
    if "topic_name" not in item_doc and "topic" in item_doc:
        item_doc["topic_name"] = item_doc["topic"]
    # Lookup or create source by name
    source_name = item_doc.get("stream") or item_doc.get("source_id")
    if source_name:
        source = await db["sources"].find_one({"name": source_name})
        if not source:
            source_id = (await db["sources"].insert_one({"name": source_name})).inserted_id
        else:
            source_id = source["_id"]
        item_doc["source_id"] = source_id
    # Set created_at and updated_at to current UTC time
    now = datetime.now(timezone.utc).isoformat()
    item_doc["created_at"] = now
    item_doc["updated_at"] = now
    result = await collection.insert_one(item_doc)
    item_doc["_id"] = result.inserted_id
    return to_str_id(item_doc) 