from database import user_collection
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, field_validator
from bson import ObjectId
from typing import Optional

app = FastAPI()

class User(BaseModel):
    name: str
    email: EmailStr
    age: # The `Optional` type hint in Python indicates that a particular argument or variable can be
    # of a specified type or `None`. In the provided code snippet, the `age` field in the `User`
    # model is defined as `Optional[int]`, which means that the `age` attribute can either be an
    # integer value or `None`.
    Optional[int] 
    @field_validator("age")
    def validate_age(cls, value: int):
        if value < 18 or value > 100:
            raise ValueError("Age must be between 18 and 100")
        return value
    
@app.get("/users/")
async def get_users() -> list[User]:
    return [user for user in user_collection.find()]

class UserResponse(User):
    id: str
@app.post("/user/")
async def create_user(user: User):
    result = user_collection.insert_one(
        user.model_dump(exclude_none=True)
    )
    user_response = UserResponse(
        id=str(result.inserted_id),
        **user.model_dump()
    )
    return user_response

@app.get("/user")
async def get_user(user_id: str) -> UserResponse:
    db_user = user_collection.find_one(
        {
            "_id": ObjectId(user_id)
            if ObjectId.is_valid(user_id)
            else None
        }
    )
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user["id"] = str(db_user["_id"])
    return UserResponse(**db_user)

