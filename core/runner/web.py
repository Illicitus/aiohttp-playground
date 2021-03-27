import logging
import socket
from importlib import import_module
from typing import (
    Any, Callable, Optional, Type, Union
)

import orjson
import uvloop

from core import config
from core.exceptions.main import ImproperlyConfigured
from core.runner.middlewares import AbstractWebAppMiddleware
from core.runner.signallers import AbstractWebAppSignaller

import aiohttp_cors
from aiohttp import web
from aiohttp.abc import AbstractAccessLogger
from aiohttp.log import access_logger
from aiohttp.web_log import AccessLogger
from aiohttp.web_routedef import RouteDef


try:
    from ssl import SSLContext
except ImportError:  # pragma: no cover
    SSLContext = Any  # type: ignore

CLIENT_SESSION = 'client_session'
DATABASE = 'db'


class WebAppApiRunner:
    aiohttp_app_related_name = 'api_runner'
    default_apps_root_directory = config.APPS_ROOT_DIRECTORY
    default_json_handler = orjson
    cors = None

    def __init__(
            self,
            *,
            loop: Optional[Any] = None,
            json_handler: Optional[Any] = None,
            signallers: Optional[tuple[Union[Type[AbstractWebAppSignaller], None], ...]] = None,
            middlewares: Optional[tuple[Union[Type[AbstractWebAppMiddleware], None], ...]] = None,
            apps_root_directory: Optional[str] = None,
    ):
        self.loop = self._get_loop_or_default(loop)
        self.json_handler = self._get_json_handler_or_default(json_handler)

        self.app = web.Application(loop=loop, debug=config.DEBUG, middlewares=middlewares)
        self.app[self.aiohttp_app_related_name] = self

        self.apps_root_directory = apps_root_directory if apps_root_directory else self.default_apps_root_directory
        self.extra = {
            'json_handler': self.json_handler,
        }

        self.signallers = signallers
        self.collect_signallers()
        self.collect_middlewares()
        self.collect_routes()
        self.setup_cors()

    @staticmethod
    def _get_loop_or_default(loop: Any) -> Any:
        return loop if loop is not None else uvloop.EventLoopPolicy()

    def _get_json_handler_or_default(self, json_handler: Any) -> Any:
        return json_handler if json_handler is not None else self.default_json_handler

    def collect_signallers(self) -> None:
        for signaller in self.signallers:
            signaller(self.app, self.extra)

    def collect_middlewares(self) -> None:
        pass

    def collect_app_routes(self, app: str) -> list[RouteDef]:
        try:
            route_conf_module = import_module(f'{self.apps_root_directory}.{app}.routes')
        except ModuleNotFoundError:
            raise ImproperlyConfigured(f'Can\'t import next {app} app routes. routes.py file is required.')
        else:
            return getattr(route_conf_module, 'routes')

    def collect_routes(self) -> None:
        apps = config.INSTALLED_APPS

        routes = []
        for app in apps:
            routes.extend(self.collect_app_routes(app))

        self.app.add_routes(routes)

    def setup_cors(self) -> None:
        self.cors = aiohttp_cors.setup(
            self.app,
            defaults={
                '*': aiohttp_cors.ResourceOptions(
                    allow_credentials=True,
                    expose_headers='*',
                    allow_headers='*',
                )
            })

        if len(list(self.app.router.routes())) == 0:
            self.collect_routes()

        for route in list(self.app.router.routes()):
            self.cors.add(route)

    def run(self,
            *,
            host: Optional[Union[str, web.HostSequence]] = None,
            port: Optional[int] = None,
            path: Optional[str] = None,
            sock: Optional[socket.socket] = None,
            shutdown_timeout: float = 60.0,
            ssl_context: Optional[SSLContext] = None,
            print: Callable[..., None] = print,
            backlog: int = 128,
            access_log_class: Type[AbstractAccessLogger] = AccessLogger,
            access_log_format: str = AccessLogger.LOG_FORMAT,
            access_log: Optional[logging.Logger] = access_logger,
            handle_signals: bool = True,
            reuse_address: Optional[bool] = None,
            reuse_port: Optional[bool] = None,
            ) -> None:

        if not port:
            port = config.PORT

        if not host:
            host = config.HOST

        return web.run_app(
            app=self.app,
            host=host,
            port=port,
            path=path,
            sock=sock,
            shutdown_timeout=shutdown_timeout,
            ssl_context=ssl_context,
            print=print,
            backlog=backlog,
            access_log_class=access_log_class,
            access_log_format=access_log_format,
            access_log=access_log,
            handle_signals=handle_signals,
            reuse_address=reuse_address,
            reuse_port=reuse_port,
        )
