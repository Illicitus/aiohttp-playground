from pydantic import BaseModel

from tortoise.contrib.pydantic import pydantic_model_creator


class EmptySerializer(BaseModel):
    pass


class PydanticSerializer:

    def __init__(self, model):
        self.pydantic_schema = pydantic_model_creator(model)

    async def dumps(self, instance):
        return await self.pydantic_schema.from_tortoise_orm(instance)
