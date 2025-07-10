from fastapi import APIRouter, HTTPException, status, Request, Query
from app.models.item import Item
from app.db import db
from pydantic import BaseModel
from app.models.subscribe_request import SubscribeRequest
from app.services.subscription_service import subscribe_user_to_topic, UserNotFoundError
from app.services.items_service import create_item as create_item_service, read_items as read_items_service, get_items_for_user, MAX_ITEMS
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
from app.services.shared_db import dead_letter_collection

router = APIRouter()

@router.post("/items")
async def create_item(item: Item):
    return await create_item_service(item)

@router.get("/items")
async def read_items(
    topic_name: str = None,
    source_name: str = None,
    start_date: str = None,
    end_date: str = None,
    skip: int = 0,
    limit: int = MAX_ITEMS,
    by_source: bool = True
):
    return await read_items_service(
        topic_name=topic_name,
        source_name=source_name,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
        by_source=by_source
    )

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
async def get_user_items(user_id: str, order_by: str = "created_at", by_source: bool = True, limit: int = MAX_ITEMS):
    return await get_items_for_user(user_id, order_by=order_by, by_source=by_source, limit=limit)

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

@router.get("/metrics")
async def metrics():
    # Count successes and failures for fetch and webhook events
    fetch_success = await db["log_events"].count_documents({"type": "fetch", "error": None})
    fetch_fail = await db["log_events"].count_documents({"type": "fetch", "error": {"$ne": None}})
    webhook_success = await db["log_events"].count_documents({"type": "webhook", "error": None})
    webhook_fail = await db["log_events"].count_documents({"type": "webhook", "error": {"$ne": None}})
    return {
        "fetch": {"success": fetch_success, "fail": fetch_fail},
        "webhook": {"success": webhook_success, "fail": webhook_fail}
    }

@router.get("/healthz")
async def healthz():
    return {"status": "ok"}

@router.get("/dead_letter")
async def get_dead_letter_events(limit: int = 20):
    cursor = dead_letter_collection.find().sort("time", -1).limit(limit)
    events = [convert_object_ids_to_str(event) async for event in cursor]
    return {"dead_letter": events} 