from pydantic import BaseModel, Field
from typing import Optional

class Source(BaseModel):
    id: Optional[str] = Field(alias="_id")
    name: str