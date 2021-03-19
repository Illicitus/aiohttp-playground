from pydantic import ValidationError

from core.responses.json import Response
from core.validators.main import (
    validation_error, Validator
)


class CreateModelMixin:
    """
    Create model instance.
    """

    async def create(self):
        data = await self.get_request_data()
        serialized_data = self.serialize_data(data)

        await self.validate_data(serialized_data)

        instance = await self.perform_create(serialized_data)
        response = await self.prepare_response(instance)

        return response

    async def perform_create(self, valid_data):
        instance = None
        return instance

    async def prepare_response(self, instance):
        return Response(instance, status_code=201)
