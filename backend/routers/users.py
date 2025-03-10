from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

router = APIRouter()

users_db = {}

SECRET_KEY = "f7e3b1"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(BaseModel):
    username: str
    email: str
    password: str
    is_admin: bool = False


class UserInDB(User):
    id: str


class Token(BaseModel):
    access_token: str
    user: dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/register")
def register_user(new_user: User):
    for user in users_db.values():
        if user.email == new_user.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    user_id = str(uuid.uuid4())
    user_in_db = UserInDB(**new_user.model_dump(), id=user_id)
    users_db[user_id] = user_in_db
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": new_user.email},
        expires_delta=access_token_expires
    )
    
    # Return token and user data (excluding password)
    user_data = user_in_db.model_dump()
    del user_data["password"]

    return {"token": access_token, "token_type": "bearer", "user": user_data}


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for u in users_db.values():
        if u.email == form_data.username:
            user = u
            break
    
    if not user or user.password != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    # Return token and user data (excluding password)
    user_data = user.model_dump()
    del user_data["password"]
    
    return {"token": access_token, "token_type": "bearer", "user": user_data}


@router.get("/user")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = None
    for u in users_db.values():
        if u.email == email:
            user = u
            break
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Return user data (excluding password)
    user_data = user.model_dump()
    del user_data["password"]
    
    return {"user": user_data}


@router.delete("/user/{user_id}")
async def delete_user(user_id: str, current_user: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(current_user, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        authenticated_user = None
        authenticated_user_id = None
        for uid, user in users_db.items():
            if user.email == email:
                authenticated_user = user
                authenticated_user_id = uid
                break

        if not authenticated_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authenticated user not found"
            )

        if user_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        # For security, only allow users to delete their own account
        # or add admin check here if needed
        if authenticated_user_id != user_id and not authenticated_user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this user"
            )
            
        deleted_user = users_db.pop(user_id)
        
        user_data = deleted_user.model_dump()
        del user_data["password"]
        
        return {
            "message": "User deleted successfully",
            "user": user_data
        }
        
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
