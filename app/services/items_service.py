from app.db import collection, db
from app.models.item import Item
from typing import List, Optional
from bson import ObjectId

MAX_ITEMS = 20

def to_str_id(doc):
    if doc is None:
        return doc
    doc = dict(doc)
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    if "topic_id" in doc and isinstance(doc["topic_id"], ObjectId):
        doc["topic_id"] = str(doc["topic_id"])
    return doc

async def create_item(item: Item):
    topic = await db["topics"].find_one({"name": item.topic_name})
    if not topic:
        topic_id = (await db["topics"].insert_one({"name": item.topic_name})).inserted_id
    else:
        topic_id = topic["_id"]
    doc = item.dict(by_alias=True, exclude={"topic_name"})
    doc["topic_id"] = topic_id
    doc.pop("_id", None)
    result = await collection.insert_one(doc)
    inserted = await collection.find_one({"_id": result.inserted_id})
    return {"status": "inserted", "item": to_str_id(inserted)}

async def read_items(topic_id: Optional[str] = None):
    query = {"topic_id": topic_id} if topic_id else {}
    cursor = collection.find(query, {"_id": 0}) if topic_id else collection.find({}, {"_id": 0})
    items = [to_str_id(item) async for item in cursor.sort("created_at", -1).limit(MAX_ITEMS)]
    return {"items": items}

async def get_items_for_user(user_id: str):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("subscribed_topics"):
        return {"items": []}
    query = {"topic_id": {"$in": user["subscribed_topics"]}}
    cursor = collection.find(query).sort("created_at", -1).limit(MAX_ITEMS)
    items = [to_str_id(item) async for item in cursor]
    return {"items": items} 