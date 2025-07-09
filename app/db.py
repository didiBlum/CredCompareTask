import mongomock

mongo_client = mongomock.MongoClient()
db = mongo_client["test_db"]
collection = db["test_collection"] 