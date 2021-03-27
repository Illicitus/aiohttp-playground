from core.responses.json import Response


class CreateModelMixin:
    """
    Create a model instance.
    """

    async def create(self):
        data = await self.get_request_data()
        serializer = self.serialize_data(data)

        await self.validate_data(serializer)

        model = self.get_serializer_model(serializer)
        instance = await self.perform_create(model, serializer)

        return await self.prepare_response(instance)

    async def perform_create(self, model, valid_data):
        return await model.create(**valid_data.dict())

    async def prepare_response(self, instance):
        return Response(
            self.serialize_data(**instance.dict()).dict(by_alias=True),
            status_code=201,
        )


class RetrieveModelMixin:
    """
    Retrieve a model instance.
    """
    pydantic_model = None

    async def retrieve(self):
        instance = await self.get_instance()

        instance = await self.instance_to_pydantic_instance(instance)
        serializer = self.serialize_data(instance.dict())

        return await self.prepare_response(serializer)

    async def prepare_response(self, serializer):
        return Response(serializer.dict(by_alias=True), status_code=201)


class UpdateModelMixin(object):
    """
    Update a model instance.
    """

    async def update(self, partial: bool = False):
        data = await self.get_request_data()
        serializer = self.serialize_data(data)

        await self.validate_data(serializer)

        instance = await self.get_instance()
        instance = await self.instance_to_pydantic_instance(instance)
        serializer = self.serialize_data(instance.dict())

        self.perform_update(serializer)

        return Response(serializer.data)

    async def prepare_response(self, serializer):
        return Response(serializer.dict(by_alias=True), status_code=201)

    async def perform_update(self, serializer):
        serializer.save()

    async def partial_update(self):
        return self.update(partial=True)
