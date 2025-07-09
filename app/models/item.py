from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Item(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    title: str
    content: str
    source_id: str
    topic_name: str
    created_at: datetime 