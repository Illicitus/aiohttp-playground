from core.validators.errors import ValidationValueError

from .models import User


async def unique_user_email(data):
    queryset = await User.filter(email=data.email).exists()

    if queryset:
        raise ValidationValueError(model=data, loc=('email',), msg='Email already exists')
