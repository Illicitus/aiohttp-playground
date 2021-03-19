class MethodHandler:
    available_methods = ('GET', 'POST', 'PATCH', 'PUT', 'DELETE')
    default_value = None

    def __init__(self, get=None, post=None, patch=None, put=None, delete=None):
        self.params = locals()

        for atr in self.__init__.__code__.co_varnames[1:]:
            self.__setattr__(str.upper(atr), self.set_attribute(atr))

    def set_attribute(self, param):
        value = self.params.get(param)

        return value if value is not None else self.default_value
