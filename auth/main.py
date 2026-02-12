from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, utils
from auth_db import get_db, create_tables, engine
from jose import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from starlette import status




SECRET_KEY = "YV7f_eutVM37pl7NXzl1-u2GPUNx_kL6lGVB1bRZAG0"
ALOGITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Helper function that take user data
def create_access_token(data: dict):
    to_encode = data.copy()
    # to_encode.update({"exp": expire})
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALOGITHM)
    return encode_jwt

app = FastAPI()

@app.post("/signup")
def register(user:schemas.UserCreate, status_code=201, db: Session = Depends(get_db)):
    # check the user exist or not
    exiting_user = db.query(models.User).filter(models.User.username== user.username).first()
    if exiting_user:
        raise HTTPException(status_code=400, detail="Username already exist")
    
    # hash the password
    hashed_pass = utils.hash_password(user.password)
    # Create a new user instance
    new_user = models.User(
        username=user.username,
        email=user.email,   
        hashed_password=hashed_pass,
        role=user.role
    )
    
    # save the user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {'id': new_user.id,"username ": new_user.username,'email':new_user.email, 'role':new_user.role,"message": "User created successfully"}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username")
    
    if not utils.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    
    token_data = {"sub": user.username, "role": user.role}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
    headers = {"www-Authenticate": "Bearer"}
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALOGITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
    except jwt.JWTError: 
        raise credentials_exception
    
    return {"username": username, "role": role, "message": "Token is valid"}


@app.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['username']}! You have accessed a protected route.", "role": current_user['role']}


def require_role(allowed_roles: list[str]):
    def role_checker(current_user: dict = Depends(get_current_user)):
        user_role = current_user.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to access this resource")
        return current_user
    return role_checker 
   
   
@app.get("/profile")
def profile(current_user: dict = Depends(require_role(["admin", "user"]))):
    return {"message": f"Hello, {current_user['username']}! This is your profile.", "role": current_user['role']}   


@app.get("/user/dashboard")
def user_dashboard(current_user: dict = Depends(require_role(["user"]))):
    return {"message": f"Welcome to the user dashboard, {current_user['username']}!", "role": current_user['role']}


@app.get("/admin/dashboard")
def admin_dashboard(current_user: dict = Depends(require_role(["admin"]))):
    return {"message": f"Welcome to the admin dashboard, {current_user['username']}!", "role": current_user['role']}

   

    
    
    

