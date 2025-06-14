from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    firstname: str
    lastname: str
    dob: str
    email: EmailStr
    password: str
 
class UserLogin(BaseModel):
    email: EmailStr
    password: str
