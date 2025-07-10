from fastapi import APIRouter, HTTPException, status, Request, Query
from app.models.item import Item
from app.db import collection, db
from pydantic import BaseModel
from app.models.subscribe_request import SubscribeRequest
from app.services.subscription_service import subscribe_user_to_topic, UserNotFoundError
from app.services.items_service import create_item as create_item_service, read_items as read_items_service, get_items_for_user
from app.services.user_service import add_user
from app.models.user import User
from app.services.webhook_service import handle_webhook_data
import logging
logger = logging.getLogger("api")
from app.models.log_event import LogEvent
from app.db import db
from datetime import datetime
from typing import Optional, List
from app.utils import convert_object_ids_to_str

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
        return await subscribe_user_to_topic(req.user_id, req.topic_name)
    except UserNotFoundError:
        raise HTTPException(status_code=404, detail="User not found")

@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    return await add_user(user)

@router.get("/users/{user_id}/items")
async def get_user_items(user_id: str):
    return await get_items_for_user(user_id)

@router.post("/webhook")
async def webhook_handler(request: Request, source: str = Query(...)):
    data = await request.json()
    logger.info(f"Received data for stream: {data}, source: {source}")
    item = await handle_webhook_data(data, source)
    return {"status": "received", "item": item}

@router.get("/logs", response_model=List[LogEvent])
async def get_logs(
    skip: int = 0,
    limit: int = 20,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source_name: Optional[str] = None,
    type: Optional[str] = None,
    include_error: Optional[bool] = None
):
    query = {}
    if start_date or end_date:
        query["time"] = {}
        if start_date:
            query["time"]["$gte"] = datetime.fromisoformat(start_date)
        if end_date:
            query["time"]["$lte"] = datetime.fromisoformat(end_date)
    if source_name:
        query["source_name"] = source_name
    if type:
        query["type"] = type
    if include_error is not None:
        if include_error:
            query["error"] = {"$ne": None}
        else:
            query["error"] = None
    cursor = db["log_events"].find(query).sort("time", -1).skip(skip).limit(limit)
    results = [LogEvent(**convert_object_ids_to_str(doc)) async for doc in cursor]
    return results 