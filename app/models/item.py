from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Item(BaseModel):
    id: Optional[str] = Field(alias="_id")
    title: str
    content: str
    source_id: str
    topic_id: str
    date_appeared: datetime 