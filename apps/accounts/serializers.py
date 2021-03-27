import re

from pydantic import (
    BaseModel, Field, ValidationError, validator
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

    @classmethod
    @validator('email')
    def validate_email(cls, value):
        if re.match(EMAIL_REGEX, value):
            return value
        return ValidationError('Wrong email.')

    @classmethod
    @validator('email')
    def normalize_email(cls, value):
        return value.lower()

    @classmethod
    @validator('password')
    def validate_password(cls, value):
        if re.match(PASSWORD_REGEX, value):
            return value
        return ValidationError('Password is too simple.')


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
    def validate_email(cls, value):
        if re.match(EMAIL_REGEX, value):
            return value
        return ValidationError('Wrong email.')

    @classmethod
    @validator('email')
    def normalize_email(cls, value):
        return value.lower()
