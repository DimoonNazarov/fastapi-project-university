import re
import uuid

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, validator

#####################################
#      BLOCK WITH API MODELS        #
####################################


class TunedModel(BaseModel):
    class Config:
        """tels pydantic to convert even non dict object to json"""
        orm_mode = True


class ShowUser(TunedModel):
    user_id: uuid.UUID
    name: str
    surname: str
    email: EmailStr
    is_active: bool


LETTER_MATCH_PARRENT = re.compile(r"^[а-яА-Яa-zA-Z\-]+$")


class UserCreate(BaseModel):
    name: str
    surname: str
    email: EmailStr

    @validator('name')
    def validate_name(cls, value):
        if not LETTER_MATCH_PARRENT.match(value):
            raise HTTPException(status_code=422, detail="Name should contain only letters")
        return value

    @validator('surname')
    def validate_surname(cls, value):
        if not LETTER_MATCH_PARRENT.match(value):
            raise HTTPException(status_code=422, detail="Name should contain only letters")
        return value




