from typing import (
    Any, Optional, Union
)

import orjson
from pydantic.json import pydantic_encoder

from core.exceptions.json import JsonHttpException

from aiohttp.typedefs import LooseHeaders
from aiohttp.web_exceptions import HTTPBadRequest


class Response(JsonHttpException):
    status_code = 200

    def __init__(
            self,
            text: Optional[Union[str, dict]] = None,
            *,
            status_code: Optional[int] = None,
            headers: Optional[LooseHeaders] = None,
            reason: Optional[str] = None,
            body: Any = None,
            content_type: Optional[str] = None,
    ):

        if status_code:
            self.status_code = status_code

        if self.status_code == HTTPBadRequest.status_code and isinstance(text, dict):
            field_errors = text.get('fields')
            if field_errors and not text.get('error'):
                text['error'] = field_errors.pop(Schema, ('Some fields have errors.',))[0]

        super().__init__(
            headers=headers,
            reason=reason,
            body=body,
            text=orjson.dumps(text).decode('utf-8'),
            content_type=content_type or self.content_type,
        )


class ErrorResponse(JsonHttpException):
    status_code = 400

    def __init__(
            self,
            text: Optional[Union[str, dict]] = None,
            *,
            status_code: Optional[int] = None,
            headers: Optional[LooseHeaders] = None,
            reason: Optional[str] = None,
            body: Any = None,
            content_type: Optional[str] = None,
    ):
        if status_code:
            self.status_code = status_code
        super().__init__(
            headers=headers,
            reason=reason,
            body=body,
            text=str(text),
            content_type=content_type or self.content_type,
        )
        self.text = orjson.dumps({'error': text or self.reason}, default=pydantic_encoder).decode('utf-8')


class NotFound(ErrorResponse):
    status_code = 404
