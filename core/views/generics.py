from pydantic import ValidationError

from core.handlers.serializers import GetSerializerClassMixin
from core.responses.json import ErrorResponse
from core.validators.main import (
    validation_error, Validator
)

from ..runner.web import WebAppApiRunner
from .mixins import CreateModelMixin

from aiohttp import web
from aiohttp_cors import CorsViewMixin


class ApiView(GetSerializerClassMixin, CorsViewMixin, web.View):
    permissions_class = None
    serializers_class = None
    validators = None

    async def get_request_data(self):
        """
        Get data from request. Default content type is JSON, otherwise override this method.
        """
        try:
            request_data = await self.request.json(
                loads=self.request.app[WebAppApiRunner.aiohttp_app_related_name].json_handler.loads,
            )
        except ValueError:
            raise ErrorResponse('Decode error! Ensure that Content-Type is application/json.')
        return request_data

    def serialize_data(self, data):
        """
        Serialize data then return pydantic object or raise ValidationError if data is wrong.
        """
        try:
            clear_data = self.get_serializer(**data)
        except ValidationError as err:
            raise ErrorResponse(validation_error(err))
        else:
            return clear_data

    def get_serializer(self, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        context = self.get_serializer_context()
        serializer = serializer_class(**kwargs)

        setattr(serializer, 'context', context)

        return serializer

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        return {
            'request': self.request,
            'view': self
        }

    async def validate_data(self, data):
        """
        Validate data using selected validators and raise an error if data is not valid.
        """
        validator = Validator(data, self.get_validators())
        await validator.validate_data()

    def get_validators(self):
        """
        Return validators if they exists or empty list
        """
        return self.validators if self.validators is not None else []


class CreateAPIView(CreateModelMixin, ApiView):
    """
    Concrete view for creating a model instance.
    """

    async def post(self):
        return await self.create()
