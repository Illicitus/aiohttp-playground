import os

from envparse import env

from core.utils.common import collect_project_models


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env.read_envfile('.env')

SECRET_KEY = 'secret'

APPS_ROOT_DIRECTORY = 'apps'

DEBUG = env.bool('DEBUG')
HOST = env.str('HOST')
PORT = env.int('PORT')

INSTALLED_APPS = (
    'accounts',
    'blog',
    'core',
)

DATABASES = {
    'connections': {
        'default': {
            'engine': 'tortoise.backends.asyncpg',
            'credentials': {
                'host': env.str('DB_HOST'),
                'port': env.int('DB_PORT'),
                'user': env.str('DB_USER'),
                'database': env.str('DB_NAME'),
                'password': env.str('DB_PASS'),
            },
            'minsize': 2,
            'maxsize': 5
        }, },
    'apps': {
        'models': {
            'models': collect_project_models(INSTALLED_APPS, BASE_DIR, APPS_ROOT_DIRECTORY),
            'default_connection': 'default',
        },
    },
}
