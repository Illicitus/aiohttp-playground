from core.typing.serializer import PydanticModel

from ..serializers.main import EmptySerializer
from .main import MethodHandler


class SerializersClass(MethodHandler):
    default_value = EmptySerializer


class GetSerializerClassMixin:
    serializers_class = None

    def get_serializer_class(self) -> PydanticModel:
        results = self.serializers_class if self.serializers_class is not None else SerializersClass()
        method = self.request.method

        assert isinstance(self.serializers_class, SerializersClass) is not None, (
            f'{self.__class__.__name__} should either include a `serializer_class` attribute,'
            f' or override the `get_serializer_class()` method.'
        )

        assert method in SerializersClass.available_methods, (
            f'Requested method unavailable, please select next one\'s: {SerializersClass.available_methods}'
        )

        return getattr(results, method)
