from abc import (
    ABC, abstractmethod
)
from typing import (
    Any, Awaitable, Dict, Optional, Union
)

from core import config

from aiohttp import (
    ClientSession, web
)

from tortoise import Tortoise


try:
    from ssl import SSLContext
except ImportError:  # pragma: no cover
    SSLContext = Any  # type: ignore

CLIENT_SESSION = 'client_session'
DATABASE = 'db'


class AbstractWebAppSignaller(ABC):
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


class WebAppSessionClientSignaller(AbstractWebAppSignaller):
    async def init(self, app: web.Application) -> None:
        self.app[CLIENT_SESSION] = ClientSession(json_serialize=self.extra['json_handler'].dumps)

    async def close(self, app: web.Application) -> None:
        await self.app[CLIENT_SESSION].close()
        await self.app[CLIENT_SESSION].wait_closed()


class WebAppTortoiseOrmSignaller(AbstractWebAppSignaller):
    async def init(self, app: web.Application, *args, **kwargs) -> None:
        engine = await Tortoise.init(config=config.DATABASES)
        self.app[DATABASE] = engine

        await Tortoise.generate_schemas()

    async def close(self, app: web.Application) -> None:
        await self.app[DATABASE].close_connections()
        await self.app[DATABASE].wait_closed()
