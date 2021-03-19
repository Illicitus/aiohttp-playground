from pydantic import ValidationError

from core.handlers.serializers import SerializersClass
from core.views.generics import (
    ApiView, CreateAPIView
)

from . import serializers
from .models import User

from aiohttp import web
from aiohttp_cors import CorsViewMixin


class CreateUser(CreateAPIView):
    serializers_class = SerializersClass(
        post=serializers.CreateUser,
    )


class RetrieveUpdateDeleteUser(CorsViewMixin, web.View):
    async def get(self):
        return await User.all()

    async def post(self):
        return await User.create(email='user@gmail.com', password='test')
