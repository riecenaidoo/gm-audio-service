from pydantic import BaseModel

class Channel(BaseModel):
    id: str
    name: str