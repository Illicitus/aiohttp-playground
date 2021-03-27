import os

from core.runner.signallers import (
    WebAppSessionClientSignaller, WebAppTortoiseOrmSignaller
)
from core.runner.web import WebAppApiRunner


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
signallers = (
    WebAppSessionClientSignaller,
    WebAppTortoiseOrmSignaller,
)

middlewares = (
    # error_middleware,
)

web_app = WebAppApiRunner(
    signallers=signallers,
    middlewares=middlewares,
)

if __name__ == '__main__':
    web_app.run()
