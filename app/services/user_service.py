from app.db import db
from app.models.user import User

def add_user(user: User):
    doc = user.dict(by_alias=True, exclude_unset=True)
    result = db["users"].insert_one(doc)
    doc["_id"] = result.inserted_id
    return {"status": "inserted", "user_id": str(result.inserted_id)} 