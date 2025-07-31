from pydantic import BaseModel
from typing import Optional
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    id: Optional[int] = None
class TaskWithId(Task):
    id: int

