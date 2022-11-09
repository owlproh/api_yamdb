from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminUserOrReadOnly


class MasterViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    mixins.DestroyModelMixin,
                    viewsets.GenericViewSet):
    """ViewSet для GET, POST, DELETE запросов."""
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
