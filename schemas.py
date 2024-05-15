from pydantic import BaseModel

class Pets(BaseModel):
    name: str
    animal: str
    checked_in: bool = False