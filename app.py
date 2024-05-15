from fastapi import FastAPI, Depends
import schemas
import models
from db import engine, SessionLocal
from sqlalchemy.orm import Session


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


#This function creates a db instance, then closes the instance.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/")
async def index():
    return "Hello World!"


@app.get("/testdb")
def get_pets(db: Session = Depends(get_db)):
    pets = db.query(models.Pets).all()
    return pets


#TODO Why can i send an int for name and animal field when I give a pydantic schema?
@app.post("/testdb")
def add_pet(pet: schemas.Pets,db: Session = Depends(get_db)):
    db_pet = models.Pets(name=pet.name, animal=pet.animal, checked_in=pet.checked_in)
    db.add(db_pet)
    db.commit()
    db.refresh(db_pet)
    return db_pet


#TODO PUT and DELETE