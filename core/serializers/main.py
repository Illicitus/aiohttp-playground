from pydantic import BaseModel

from core.typing.orm import TortoiseModel

from tortoise.contrib.pydantic import pydantic_model_creator


class EmptySerializer(BaseModel):
    pass


class PydanticSerializer:

    def __init__(self, model: TortoiseModel):
        self.pydantic_schema = pydantic_model_creator(model)

    async def dumps(self, instance: TortoiseModel):
        return await self.pydantic_schema.from_tortoise_orm(instance)
