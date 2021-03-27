from importlib import import_module
from os import path
from typing import (
    List, Optional
)

from ..exceptions.main import ImproperlyConfigured


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError as err:
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError as err:
        raise ImportError('Module "%s" does not define a "%s" attribute/class' % (
            module_path, class_name)
                          ) from err


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
