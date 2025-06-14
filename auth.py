from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from database import add_user, get_user_by_email, verify_user, log_login_attempt
from pydantic import BaseModel
from auth_service import create_access_token
from datetime import timedelta, date
from passlib.context import CryptContext

class UserSignup(BaseModel):
    email: str
    password: str
    firstName: str
    lastName: str
    dateOfBirth: date

class UserLogin(BaseModel):
    email: str
    password: str

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/signup")
def signup(user: UserSignup):
    if get_user_by_email(user.email):
        raise HTTPException(status_code=400, detail="البريد الإلكتروني مسجل بالفعل")
    
    success = add_user(
        email=user.email,
        password=user.password,
        first_name=user.firstName,
        last_name=user.lastName,
        date_of_birth=str(user.dateOfBirth),
        is_admin=False
    )
    if not success:
        raise HTTPException(status_code=400, detail="فشل في إنشاء المستخدم")

    return {"message": "تم إنشاء المستخدم بنجاح"}

@router.post("/login")
async def login(request: Request, user_data: UserLogin):
    user = verify_user(user_data.email, user_data.password)
    if not user:
        log_login_attempt(user_data.email, False, request.client.host)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    log_login_attempt(user_data.email, True, request.client.host)
    access_token = create_access_token({"sub": user["email"]}, timedelta(minutes=30))
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "email": user["email"],
            "is_admin": user["is_admin"]
        }
    }