from fastapi import APIRouter, HTTPException, status
from app.models.item import Item
from app.db import collection, db
from pydantic import BaseModel
from app.models.subscribe_request import SubscribeRequest
from app.services.subscription_service import subscribe_user_to_topic, UserNotFoundError
from app.services.items_service import create_item as create_item_service, read_items as read_items_service
from app.services.user_service import add_user
from app.models.user import User

router = APIRouter()

@router.post("/items")
async def create_item(item: Item):
    return await create_item_service(item)

@router.get("/items")
async def read_items(topic_id: str = None):
    return await read_items_service(topic_id)

@router.post("/subscribe")
async def subscribe_to_topic(req: SubscribeRequest):
    try:
        return subscribe_user_to_topic(req.user_id, req.topic_name)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    return add_user(user) 