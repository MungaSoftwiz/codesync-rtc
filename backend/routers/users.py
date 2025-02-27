from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class User(BaseModel):
    username: str
    email: str
    password: str


users_db = {}


@router.post("/register")
def register_user(user: User):
    if user.email in users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    users_db[user.email] = user
    return {"message": "User registered successfully"}


@router.post("/login")
def login_user(user: User):
    if user.email not in users_db or users_db[user.email].password != user.password:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}
