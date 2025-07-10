from app.db import items_collection, db
from app.models.item import Item
from typing import List, Optional
from bson import ObjectId
from app.utils import convert_object_ids_to_str
from datetime import datetime

MAX_ITEMS = 20

async def create_item(item: Item):
    topic = await db["topics"].find_one({"name": item.topic_name})
    if not topic:
        topic_id = (await db["topics"].insert_one({"name": item.topic_name})).inserted_id
    else:
        topic_id = topic["_id"]
    doc = item.dict(by_alias=True, exclude={"topic_name"})
    doc["topic_id"] = topic_id
    doc.pop("_id", None)
    result = await items_collection.insert_one(doc)
    inserted = await items_collection.find_one({"_id": result.inserted_id})
    return {"status": "inserted", "item": convert_object_ids_to_str(inserted)}

async def query_items(
    query: dict,
    skip: int = 0,
    limit: int = MAX_ITEMS,
    by_source: bool = True
):
    if by_source:
        sources = await items_collection.distinct("source_name", query)
        result = {}
        for source in sources:
            source_query = {**query, "source_name": source}
            cursor = items_collection.find(source_query).sort("created_at", -1).limit(limit)
            items = [convert_object_ids_to_str(item) async for item in cursor]
            result[source] = items
        return result
    cursor = items_collection.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit)
    items = [convert_object_ids_to_str(item) async for item in cursor]
    return {"items": items}

async def read_items(
    topic_name: Optional[str] = None,
    source_name: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    skip: int = 0,
    limit: int = MAX_ITEMS,
    by_source: bool = True
):
    query = {}
    if topic_name:
        query["topic_name"] = topic_name
    if source_name:
        query["source_name"] = source_name
    if start_date or end_date:
        query["created_at"] = {}
        if start_date:
            query["created_at"]["$gte"] = start_date
        if end_date:
            query["created_at"]["$lte"] = end_date
    return await query_items(query, skip=skip, limit=limit, by_source=by_source)

async def get_items_for_user(user_id: str, order_by: str = "created_at", by_source: bool = True, limit: int = MAX_ITEMS):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user or not user.get("subscribed_topics"):
        return {"items": []}
    if by_source:
        query = {"topic_id": {"$in": user["subscribed_topics"]}}
        return await query_items(query, skip=0, limit=limit, by_source=True)
    if order_by == "topic_first_seen":
        # Find first appearance date for each topic
        topic_ids = user["subscribed_topics"]
        topic_first_seen = {}
        for topic_id in topic_ids:
            doc = await items_collection.find_one({"topic_id": topic_id}, sort=[("created_at", 1)])
            if doc:
                topic_first_seen[topic_id] = doc["created_at"]
            else:
                topic_first_seen[topic_id] = None
        # Order topics by first seen date
        ordered_topics = [tid for tid, _ in sorted(topic_first_seen.items(), key=lambda x: (x[1] is None, x[1]))]
        # For each topic, get items ordered by created_at desc
        items = []
        for topic_id in ordered_topics:
            cursor = items_collection.find({"topic_id": topic_id}).sort("created_at", -1)
            items.extend([convert_object_ids_to_str(item) async for item in cursor])
        return {"items": items}
    else:
        query = {"topic_id": {"$in": user["subscribed_topics"]}}
        return await query_items(query, skip=0, limit=limit, by_source=False) 