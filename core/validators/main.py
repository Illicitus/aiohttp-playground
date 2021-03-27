import inspect
from typing import Callable

from pydantic import ValidationError

from core.responses.json import ErrorResponse

from .errors import unpack_error_details


class Validator:

    def __init__(self, data, validators: list[Callable]):
        self.data = data
        self.validators = validators

    async def validate_data(self) -> None:
        for validator in self.validators:
            try:
                if inspect.iscoroutinefunction(validator):
                    await validator(self.data)
                else:
                    validator(self.data)
            except ValidationError as err:
                raise ErrorResponse(unpack_error_details(err))
