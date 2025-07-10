class UserNotFoundError(Exception):
    pass

from fastapi import HTTPException
from app.db import db
from bson import ObjectId

async def subscribe_user_to_topic(user_id: str, topic_name: str):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise UserNotFoundError()
    # Ensure topic exists
    topic = await db["topics"].find_one({"name": topic_name})
    if not topic:
        await db["topics"].insert_one({"name": topic_name})
    # Store topic_name in user's subscribed_topics
    if topic_name not in user.get("subscribed_topics", []):
        await db["users"].update_one({"_id": ObjectId(user_id)}, {"$push": {"subscribed_topics": topic_name}})
    return {"status": "subscribed", "user_id": user_id, "topic_name": topic_name} 