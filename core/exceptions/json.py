from aiohttp.web_exceptions import HTTPException


class JsonHttpException(HTTPException):
    content_type = 'application/json'
