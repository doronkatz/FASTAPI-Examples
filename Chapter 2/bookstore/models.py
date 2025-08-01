from pydantic import BaseModel, Field
class Book(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=50)
    year: int = Field(gt=1900, le=2025)
    

class BookResponse(BaseModel):
    author: int
    title: str