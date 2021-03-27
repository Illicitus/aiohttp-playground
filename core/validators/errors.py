from typing import Tuple

from pydantic import ValidationError
from pydantic.error_wrappers import ErrorWrapper
from pydantic.errors import PydanticValueError


class CoreValidationValueError(PydanticValueError):
    def __init__(self, msg):
        super().__init__()
        self.msg_template = msg


class ValidationValueError(ValidationError):

    def __init__(self, model: 'ModelOrDc', loc: Tuple[str], msg: str):
        errors = [ErrorWrapper(CoreValidationValueError(msg=msg), loc=loc)]

        super().__init__(errors=errors, model=model)


def unpack_error_details(error: ValidationError) -> str:
    return error.errors()
