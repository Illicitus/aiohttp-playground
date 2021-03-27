from abc import (
    ABC, abstractmethod
)
from asyncio import CancelledError
from typing import (
    Awaitable, Dict, Optional, Union
)

from ..responses.json import ErrorResponse

from aiohttp import web


# TODO typing
@web.middleware
async def error_middleware(request, handler):
    request.payload = {}
    request.user_id = None

    try:
        return await handler(request)
    except web.HTTPException as ex:
        ex_status = ex.status
        if ex_status in (404, 405) and not isinstance(ex, ErrorResponse):
            raise ErrorResponse(status_code=ex_status)
        elif ex_status >= 500:
            raven_client = request.config_dict.get('raven_client')
            if raven_client:
                raven_client.capture_request_exception(request)
        raise
    except CancelledError:
        raise
    except:
        raven_client = request.config_dict.get('raven_client')
        if raven_client:
            raven_client.capture_request_exception(request)
        raise


class AbstractWebAppMiddleware(ABC):
    def __init__(self, app: Union[web.Application, Awaitable[web.Application]], extra: Optional[Dict] = None):
        self.app = app
        self.extra = extra

        self.setup()

    @abstractmethod
    async def init(self, app: web.Application) -> None:
        pass

    @abstractmethod
    async def close(self, app: web.Application) -> None:
        pass

    def setup(self) -> None:
        self.app.on_startup.append(self.init)
        self.app.on_cleanup.append(self.close)
