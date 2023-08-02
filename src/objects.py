from pydantic import BaseModel


class User(BaseModel):
    encrypted: str
    # full_name: str
    # email: str
    # password: str
    # dob: str
    # phone: str
    # location: str = ""
