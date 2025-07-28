from pydantic import BaseModel

class Server(BaseModel):
    id: str
    name: str