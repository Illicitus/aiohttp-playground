from tortoise import fields
from tortoise.models import Model


class AbstractTime(Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
        ordering = ('id',)


class User(AbstractTime):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=250, index=True)
    password = fields.TextField()

    first_name = fields.TextField(default='')
    last_name = fields.TextField(default='')

    class Meta:
        table = 'accounts_user'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
