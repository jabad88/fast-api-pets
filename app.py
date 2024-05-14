from fastapi import FastAPI
# from . import schemas, models
from db import engine, sessionmaker,SessionLocal
from sqlalchemy.orm import Session

#TODO Connect db to app, confirm if pydantic is supposed to match models

# models.Base.metadata.create_all(engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def index():
    return "Hello World!"

# @app.post("/create_animal")
# def create(request:schemas.PetsBase, db:Session):
#     pass
