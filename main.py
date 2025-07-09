from fastapi import FastAPI
import asyncio
import mongomock
from fastapi import Request
from pydantic import BaseModel

app = FastAPI()

mongo_client = mongomock.MongoClient()
db = mongo_client["test_db"]
collection = db["test_collection"]

class Item(BaseModel):
    name: str
    value: int

@app.get("/")
async def hello_world():
    return {"message": "hello world"}

@app.post("/items")
async def create_item(item: Item):
    doc = item.dict()
    collection.insert_one(doc)
    return {"status": "inserted", "item": doc}

@app.get("/items")
async def read_items():
    items = list(collection.find({}, {"_id": 0}))
    return {"items": items} 