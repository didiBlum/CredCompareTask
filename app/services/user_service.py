from app.db import db
from app.models.user import User

def add_user(user: User):
    existing = db["users"].find_one({"_id": user.id})
    if existing:
        return {"status": "exists", "user": existing}
    doc = user.dict(by_alias=True)
    db["users"].insert_one(doc)
    return {"status": "inserted", "user": doc} 