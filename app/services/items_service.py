from app.db import collection, db
from app.models.item import Item
from typing import List, Optional

def create_item(item: Item):
    # Find or create topic by name
    topic = db["topics"].find_one({"name": item.topic_name})
    if not topic:
        topic_id = db["topics"].insert_one({"name": item.topic_name}).inserted_id
    else:
        topic_id = topic["_id"]
    doc = item.dict(by_alias=True, exclude={"topic_name"})
    doc["topic_id"] = topic_id
    collection.insert_one(doc)
    return {"status": "inserted", "item": doc}

def read_items(topic_id: Optional[str] = None):
    query = {"topic_id": topic_id} if topic_id else {}
    items = list(collection.find(query, {"_id": 0}).sort("created_at", -1).limit(20))
    return {"items": items} 