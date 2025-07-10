from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class LogEvent(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    source_name: str
    time: datetime
    items_saved: int
    error: Optional[str] = None
    type: Literal["fetch", "webhook"] 