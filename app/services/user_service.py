from app.db import db
from app.models.user import User
from app.utils import convert_object_ids_to_str
from bson import ObjectId

async def add_user(user: User):
    doc = user.dict(by_alias=True, exclude_unset=True)
    doc.pop("_id", None)
    result = await db["users"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return {"status": "inserted", "user_id": str(result.inserted_id)}

async def get_user_by_id(user_id: str):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        return None
    return convert_object_ids_to_str(user) 