from fastapi import APIRouter, HTTPException
from app.models.item import Item
from app.db import collection, db
from pydantic import BaseModel
from app.models.subscribe_request import SubscribeRequest
from app.services.subscription_service import subscribe_user_to_topic, UserNotFoundError
from app.services.items_service import create_item, read_items

router = APIRouter()

@router.post("/items")
async def create_item(item: Item):
    return create_item(item)

@router.get("/items")
async def read_items(topic_id: str = None):
    return read_items(topic_id)

@router.post("/subscribe")
async def subscribe_to_topic(req: SubscribeRequest):
    try:
        return subscribe_user_to_topic(req.user_id, req.topic_name)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found") 