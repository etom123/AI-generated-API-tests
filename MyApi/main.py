from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

class User(BaseModel):
    name: str
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    age: int

@app.post("/users", response_model=UserResponse)
def create_user(user: User):
    return {"id": 1, "name": user.name, "age": user.age}
