from pydantic import BaseModel

class SubscribeRequest(BaseModel):
    user_id: str
    topic_name: str 