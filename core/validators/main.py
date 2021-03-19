import inspect

import orjson
from pydantic import ValidationError
from pydantic.json import pydantic_encoder

from core.responses.json import ErrorResponse


def validation_error(error: ValidationError) -> str:
    return str(error.errors())


class Validator:

    def __init__(self, data, validators):
        self.data = data
        self.validators = validators

    async def validate_data(self):
        for validator in self.validators:
            try:
                if inspect.iscoroutinefunction(validator):
                    await validator(self.data)
                else:
                    validator(self.data)
            except ValidationError as err:
                raise ErrorResponse(validation_error(err))
