from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from models.user import UserCreate, UserLogin, UserResponse
from models.user import User as UserModel
from utils.auth import get_password_hash, verify_password, create_access_token
from utils.dependencies import get_current_user
import os
from motor.motor_asyncio import AsyncIOMotorClient

router = APIRouter(prefix="/auth", tags=["authentication"])

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

@router.post("/register", response_model=UserResponse)
async def register(user_create: UserCreate):
    existing_user = await db.users.find_one({"email": user_create.email}, {"_id": 0})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    user_dict = user_create.model_dump()
    hashed_password = get_password_hash(user_dict.pop("password"))
    
    user = UserModel(**user_dict, hashed_password=hashed_password)
    doc = user.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    
    await db.users.insert_one(doc)
    
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company=user.company,
        created_at=user.created_at,
        is_active=user.is_active
    )

@router.post("/login")
async def login(user_login: UserLogin):
    user_doc = await db.users.find_one({"email": user_login.email}, {"_id": 0})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(user_login.password, user_doc['hashed_password']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user_doc['id']})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user_doc['id'],
            "email": user_doc['email'],
            "full_name": user_doc['full_name'],
            "company": user_doc.get('company')
        }
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user_id: str = Depends(get_current_user)):
    user_doc = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user_doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if isinstance(user_doc['created_at'], str):
        from datetime import datetime
        user_doc['created_at'] = datetime.fromisoformat(user_doc['created_at'])
    
    return UserResponse(**user_doc)