from os import path
from typing import (
    List, Optional
)

from .exceptions.main import ImproperlyConfigured


def is_path_exists(selected_path: str) -> bool:
    return path.exists(selected_path)


def collect_project_models(
        installed_apps: List[str],
        base_dir: str,
        apps_root_directory: str,
        include_aerich: Optional[bool] = True,
):
    result = []

    for app in installed_apps:
        model_path = path.join(base_dir, apps_root_directory, app, 'models.py')

        if not is_path_exists(model_path):
            raise ImproperlyConfigured(f'Next app models.py doesn\'t exits: {app}')

        result.append('.'.join([apps_root_directory, app, 'models']))

    if include_aerich:
        result.append('aerich.models')

    return result
