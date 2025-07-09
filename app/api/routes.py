from fastapi import APIRouter
from app.models.item import Item
from app.db import collection

router = APIRouter()

@router.post("/items")
async def create_item(item: Item):
    doc = item.dict()
    collection.insert_one(doc)
    return {"status": "inserted", "item": doc}

@router.get("/items")
async def read_items():
    items = list(collection.find({}, {"_id": 0}))
    return {"items": items} 