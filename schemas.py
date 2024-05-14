from pydantic import BaseModel

class PetsBase(BaseModel):
    name: str
    animal: str
    checked_in: bool = False