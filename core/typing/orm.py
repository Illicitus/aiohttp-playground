from typing import TypeVar

from tortoise.models import Model


TortoiseModel = TypeVar('TortoiseModel', bound=Model)
