from pydantic import BaseModel


class User(BaseModel):
    encrypted: str


class DayDataObj(BaseModel):
    encrypted: str
