from pydantic import BaseModel,Field
from typing import Annotated

class PathParam(BaseModel):
    id: Annotated[int, Field(strict=True, gt=0)]