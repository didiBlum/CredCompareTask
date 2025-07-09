from pydantic import BaseModel, Field
from typing import Optional

class Topic(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str