import router_example
from fastapi import FastAPI

app = FastAPI()
app.include_router(router_example.router)
@app.get("/")
async def root():
    return {"message": "Hello, World!"}