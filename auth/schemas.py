from pydantic import BaseModel, EmailStr

# schemas for new user create
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"
    
# schemas for userlogin
    
class UserLogin(BaseModel):
    username: str
    password: str
    