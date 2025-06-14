from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

# إعداد المتغيرات السرّية
SECRET_KEY = os.getenv("SECRET_KEY", "a3f1c2e45b6d789a123456789abcdef098765432123456789abcdef0987654321")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# إعداد التشفير
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# توليد هاش لكلمة المرور
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# التحقق من تطابق كلمة المرور
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# توليد JSON Web Token (JWT)
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt