from pydantic import ValidationError

from core.handlers.serializers import GetSerializerClassMixin
from core.orm.shortcuts import get_object_or_404
from core.responses.json import ErrorResponse
from core.validators.main import (
    unpack_error_details, Validator
)

from ..runner.web import WebAppApiRunner
from .mixins import (
    CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
)

from aiohttp import web
from aiohttp_cors import CorsViewMixin


class ApiView(GetSerializerClassMixin, CorsViewMixin, web.View):
    permissions_class = None
    serializers_class = None
    validators = None
    lookup_field = 'id'
    lookup_url_kwarg = None
    pydantic_model = None

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
            raise ErrorResponse(unpack_error_details(err))
        else:
            return clear_data

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        serializer = serializer_class(*args, **kwargs)

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

    @staticmethod
    def get_serializer_model(serializer):
        model = getattr(serializer.Config, 'model', None)
        assert model is not None, 'Serializer doesn\'t include model.'

        return model

    async def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.
        """
        raise NotImplementedError(
            f'{self.__class__.__name__}'
            f' should override the `get_queryset()` method.'
        ) or None

    async def get_instance(self):
        queryset = await self.get_queryset()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        if lookup_url_kwarg not in self.request.match_info:
            raise NotImplementedError(
                f'Expected view {self.__class__.__name__} to be called with a URL keyword argument '
                f'named {lookup_url_kwarg}. Fix your URL conf, or set the `.lookup_field` '
                f'attribute on the view correctly.'
            )

        filter_kwargs = {self.lookup_field: self.request.match_info[lookup_url_kwarg]}
        obj = await get_object_or_404(queryset, **filter_kwargs)

        return obj

    async def instance_to_pydantic_instance(self, instance):
        if not self.pydantic_model:
            raise NotImplementedError(
                f'{self.__class__.__name__}'
                f' should either include a `pydantic_model` attribute.'
            )
        return await self.pydantic_model.dumps(instance)


class CreateAPIView(CreateModelMixin, ApiView):
    """
    Concrete view for creating a model instance.
    """

    async def post(self):
        return await self.create()


class RetrieveAPIView(RetrieveModelMixin, ApiView):
    """
    Concrete view for retrieving a model instance.
    """

    async def get(self):
        return await self.retrieve()


class UpdateAPIView(UpdateModelMixin, ApiView):
    """
    Concrete view for updating a model instance.
    """

    def put(self):
        return self.update()

    def patch(self):
        return self.partial_update()

# class RetrieveUpdateAPIView(RetrieveModelMixin, UpdateModelMixin, ApiView):
#     """
#     Concrete view for retrieving and updating a model instance.
#     """
#
#     async def get(self):
#         return await self.retrieve()
#
#     async def put(self):
#         return await self.update()
