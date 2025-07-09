import os
from mongomock_motor import AsyncMongoMockClient


mongo_client = AsyncMongoMockClient()
db = mongo_client["test_db"]
collection = db["test_collection"] 