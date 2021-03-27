import re

from pydantic import (
    BaseModel, Field, validator
)

from .models import User


EMAIL_REGEX = '^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,16}$'
PASSWORD_REGEX = '^(?=.*\d).{8,128}$'
EMPTY_STRING = ''


class CreateUser(BaseModel):
    email: str
    password: str

    class Config:
        model = User

    @validator('email')
    @classmethod
    def validate_email(cls, value: str) -> str:
        if re.match(EMAIL_REGEX, value):
            return value
        raise ValueError('Incorrect email.')

    @validator('email')
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()

    @validator('password')
    @classmethod
    def validate_password(cls, value: str) -> str:
        if re.match(PASSWORD_REGEX, value):
            return value
        raise ValueError('Password is too simple.')


class UserBase(BaseModel):
    id: int
    email: str
    first_name: str = Field(EMPTY_STRING, alias='firstName')
    last_name: str = Field(EMPTY_STRING, alias='lastName')


class LoginUser(BaseModel):
    email: str
    password: str

    @classmethod
    @validator('email')
    def validate_email(cls, value: str) -> str:
        if re.match(EMAIL_REGEX, value):
            return value
        raise ValueError('Wrong email.')

    @classmethod
    @validator('email')
    def normalize_email(cls, value: str) -> str:
        return value.lower()
