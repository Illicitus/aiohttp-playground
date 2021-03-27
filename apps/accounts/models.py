from typing import (
    Any, Type
)

from apps.core.models import AbstractTime
from core.hashers import (
    check_password, make_password
)
from core.serializers.main import PydanticSerializer

from tortoise import fields
from tortoise.models import MODEL


class User(AbstractTime):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=250, index=True)
    password = fields.TextField()
    _password = None

    first_name = fields.TextField(default='')
    last_name = fields.TextField(default='')

    class Meta:
        table = 'accounts_user'

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    @classmethod
    async def create(cls: Type[MODEL], **kwargs: Any) -> MODEL:
        # Hash password before saving the User object
        kwargs['password'] = cls.hash_password(kwargs['password'])

        instance = cls(**kwargs)
        instance._saved_in_db = False
        db = kwargs.get("using_db") or cls._meta.db
        await instance.save(using_db=db, force_create=True)
        return instance

    @staticmethod
    def hash_password(raw_password):
        return make_password(raw_password)

    def check_password(self, raw_password):
        """
        Return a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        return check_password(raw_password, self.password)


UserPydantic = PydanticSerializer(User)
