from core.handlers.serializers import SerializersClass
from core.orm.shortcuts import get_object_or_404
from core.responses.json import (
    ErrorResponse, Response
)
from core.typing.orm import TortoiseModel
from core.validators.errors import (
    unpack_error_details, ValidationValueError
)
from core.views.generics import (
    ApiView, CreateAPIView, RetrieveAPIView
)

from . import serializers
from .models import (
    User, UserPydantic
)
from .validators import unique_user_email


class CreateUser(CreateAPIView):
    serializers_class = SerializersClass(
        post=serializers.CreateUser,
    )
    validators = (unique_user_email,)

    async def prepare_response(self, instance: TortoiseModel):
        instance = await UserPydantic.dumps(instance)
        return Response(
            serializers.UserBase(**instance.dict()).dict(by_alias=True),
            status_code=201,
        )


class LoginUser(ApiView):
    pydantic_model = UserPydantic
    serializers_class = SerializersClass(
        post=serializers.LoginUser,
    )

    async def post(self):
        data = await self.get_request_data()
        serializer = self.serialize_data(data)

        await self.validate_data(serializer)

        queryset = User.filter(email__icontains=serializer.email)
        instance = await get_object_or_404(queryset)
        if not instance.check_password('test'):
            err = ValidationValueError(model=serializer, loc=('password',), msg='Incorrect password')
            raise ErrorResponse(unpack_error_details(err))

        return Response({})


class RetrieveUpdateDeleteUser(RetrieveAPIView):
    pydantic_model = UserPydantic
    serializers_class = SerializersClass(
        get=serializers.UserBase,
    )

    async def get_queryset(self):
        return User.filter()
