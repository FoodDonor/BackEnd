from pydantic import BaseModel


class User(BaseModel):
    encrypted: str
    # Register user:
        # full_name: str
        # email: str [OPTOINAL]
        # password: str
        # dob: str
        # phone: str [MANDATORY]
        # zip: str [MANDATORY]
        # location: str = ""
    # Login user:
        # access: str ### email or phone
        # password: str

class UpdateObj(BaseModel):
    ...
