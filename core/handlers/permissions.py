from .main import MethodHandler


class PermissionsClass(MethodHandler):
    default_value = api_settings.DEFAULT_PERMISSION_CLASSES


class GetPermissionsMixin:
    permissions_class = None

    def get_permissions(self):
        results = self.permissions_class if self.permissions_class is not None else PermissionsClass()
        method = self.request.method

        assert isinstance(self.permissions_class, PermissionsClass) is not None, (
            f'{self.__class__.__name__} should either include a `permission_classes` attribute,'
            f' or override the `get_permissions()` method.'
        )

        assert method in PermissionsClass.available_methods, (
            f'Requested method unavailable, please select next one\'s: {PermissionsClass.available_methods}'
        )

        return [permission() for permission in getattr(results, method)]
