from pydantic import BaseModel


class User(BaseModel):
    encrypted: str
    # Register user:
    # name: str
    # email: str [OPTOINAL]
    # password: str
    # dob: str
    # phone: str [MANDATORY]
    # zip: str [MANDATORY]
    # location: str = ""

    # Login user:
    # access: str ### email or phone
    # password: str


class DayDataObj(BaseModel):
    encrypted: str
    # should contain:
    # date: `mm-dd-yyyy`
    # num_fed: int
    # kgs_fed: int
    # kgs_Wasted: int
    # manpower: int
