from rest_framework import viewsets


class CustomResponseMixin(viewsets.ModelViewSet):
    list_serializer_class = None
    retrieve_serializer_class = None

    def get_serializer_class(self):
        """ Custom class to update action wise response """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )
        if self.action in ['create', 'update', 'delete'] and self.serializer_class:
            return self.serializer_class
        if self.action in ['retrieve', ] and self.retrieve_serializer_class:
            return self.retrieve_serializer_class
        if self.action in ['list'] and self.list_serializer_class:
            return self.list_serializer_class
        return self.serializer_class


class ReadOnlyCustomResponseMixin(viewsets.ReadOnlyModelViewSet):
    retrieve_serializer_class = None

    def get_serializer_class(self):
        """ Custom class to update action wise response """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )
        if self.action in ['retrieve', ] and self.retrieve_serializer_class:
            return self.retrieve_serializer_class
        return self.serializer_class
