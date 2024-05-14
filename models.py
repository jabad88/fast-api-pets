from sqlalchemy import Column, String, Integer, Boolean
from db import Base


class Pets(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    animal = Column(String,nullable=False)
    checked_in = Column, Boolean(default = False)