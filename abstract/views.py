from rest_framework import viewsets, status
from rest_framework.response import Response


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(data={'message': "Successfully created"}, status=status.HTTP_201_CREATED)


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(status=status.HTTP_200_OK, data={'message': "Successfully updated"})



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


