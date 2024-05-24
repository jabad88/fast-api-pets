from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Annotated, Union
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt
from passlib.context import CryptContext

#private imports
import schemas
import models
from db import engine, SessionLocal

SECRET_KEY = "961db7cfe3697c1f5dc0c1ca8e07b280df71b055bb309a8bad20f10f6e705c2e"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: 30

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret88",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}


app = FastAPI()



models.Base.metadata.create_all(bind=engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def fake_hash_password(password: str):
    return "fakehashed" + password



def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

#This function creates a db instance, then closes the instance.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class User(BaseModel):
    username: str
    email:  EmailStr
    full_name: str
    disabled: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str


def fake_decode_token(token):
    return User(username=token+"fakedecoded", email="john@example.com",full_name="John Doe")

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    user = fake_decode_token(token)
    if not user:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate":"Bearer"},
        )

    return user

async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Invalid User")
    return current_user



####CRUD functionality####
@app.get("/")
async def index():
    return "Hello World!"


@app.get("/testdb")
def get_pets(db: Session = Depends(get_db)):
    pets = db.query(models.Pets).all()
    return pets


@app.post("/testdb")
def add_pet(pet: schemas.Pets,db: Session = Depends(get_db)):
    db_pet = models.Pets(name=pet.name, animal=pet.animal, checked_in=pet.checked_in)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


@app.delete("/testdb/{id}")
def delete_pet(id: int, db: Session = Depends(get_db)):
    db_pet = db.query(models.Pets).filter(models.Pets.id == id).first()
    db.delete(db_pet)
    db.commit()
    return {"message": f"Pet with id {id} was successfully deleted"}

#TODO make another schema to only update the name
@app.put("/testdb/{id}")
def update_pet(id: int, pet: schemas.Pets ,db: Session = Depends(get_db)):
    db_pet = db.query(models.Pets).filter(models.Pets.id == id).first()
    db_pet.name = pet.name
    db_pet.animal = pet.animal
    db.commit()
    return {"message": f"Pet with id {id} was successfully updated"}


###END CRUD FUNCTIONALITY###

#TODO implement some form of authorization? Who is allowed to make these changes to my db?



@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(oauth2_scheme)]):
    return current_user

@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    print(user_dict)
    user=UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    print(hashed_password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    return {"access_token": user.username, "token_type": "bearer"}