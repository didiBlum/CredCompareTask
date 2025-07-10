import os
from mongomock_motor import AsyncMongoMockClient
import asyncio


mongo_client = AsyncMongoMockClient()
db = mongo_client["test_db"]
items_collection = db["test_collection"]

# Ensure indexes for efficient queries
async def ensure_indexes():
    await items_collection.create_index("topic_name")
    await items_collection.create_index("source_name")
    await items_collection.create_index("created_at")
    await items_collection.create_index([("topic_name", 1), ("created_at", -1)])
    await items_collection.create_index([("source_name", 1), ("created_at", -1)])

 