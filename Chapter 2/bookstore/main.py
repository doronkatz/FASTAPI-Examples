from fastapi import FastAPI, HTTPException
from starlette.responses import JSONResponse
from models import Book, BookResponse

app = FastAPI()
@app.get("/books/{book_id}")
async def read_book(book_id: int):
    return {
        "book_id": book_id,
        "title": "Sample Book Title",
        "author": "Sample Author"
    }

@app.get("/books")
async def read_books(year: int = None):
    if year:
        return {
            "year": year,
            "books": [
                {"book_id": 1, "title": "Sample Book Title 1", "author": "Sample Author 1"},
                {"book_id": 2, "title": "Sample Book Title 2", "author": "Sample Author 2"}
            ]
        }
    return {"books": ["All Books"]}

@app.post("/book")
async def create_book(book: Book):
    return book

@app.put("/allbooks")
async def read_all_books() -> list[BookResponse]:
    return [
        {"author": "Sample Author 1", "title": "Sample Book Title 1"},
        {"author": "Sample Author 2", "title": "Sample Book Title 2"}
    ]

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
