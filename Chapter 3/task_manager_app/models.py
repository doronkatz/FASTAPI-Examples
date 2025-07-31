from pydantic import BaseModel
from typing import Optional
class Task(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    id: Optional[int] = None
class TaskWithId(Task):
    id: int
class TaskV2(BaseModel):
    title: str
    description: Optional[str] = None
    status: Optional[str] = None
    id: Optional[int] = None
    priority: Optional[str] | None = "lower"

class TaskV2WithId(TaskV2):
    id: int
class UpdateTask(BaseModel):
    title: str
    description: str | None = None
    status: str | None = None