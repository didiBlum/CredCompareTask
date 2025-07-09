from pydantic import BaseModel, Field
from typing import List, Optional

class User(BaseModel):
    id: Optional[str] = Field(alias="_id")
    email: str
    name: Optional[str]
    subscribed_topics: List[str] = [] 