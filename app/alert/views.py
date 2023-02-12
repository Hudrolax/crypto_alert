"""
Views for the alert APIs.
"""
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
# from rest_framework.decorators import action
# from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Alert, Symbol
from alert import serializers


@extend_schema_view(list=extend_schema(parameters=[
    OpenApiParameter(
        'symbols',
        OpenApiTypes.STR,
        description='Comma separated list of symbols filter.'),
    OpenApiParameter(
        'active',
        OpenApiTypes.BOOL,
        description='Bool parameter.'),
]))
class AlertViewSet(viewsets.ModelViewSet):
    """View for manage alert APIs."""

    serializer_class = serializers.AlertSerializer
    queryset = Alert.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _active_param_to_bool(self, qs: str) -> bool:
        """Convert a active param to bool."""
        return True if qs == 'true' else False

    def get_queryset(self):
        """Retrieve alerts for authenticated user."""
        symbols = self.request.query_params.get('symbols')  # type: ignore
        active = self.request.query_params.get('active')  # type: ignore
        queryset = self.queryset
        # filters
        if symbols:
            symbol_list = symbols.split(',')
            queryset = queryset.filter(symbol__in=symbol_list)
        if active:
            active_bool = self._active_param_to_bool(active)
            queryset = queryset.filter(is_active=active_bool)

        return queryset.filter(
            user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        return self.serializer_class

    def perform_create(self, serializer) -> None:
        serializer.save(user=self.request.user)


@extend_schema_view(list=extend_schema(parameters=[
    OpenApiParameter(
        'symbols',
        OpenApiTypes.STR,
        description='Comma separated list of symbols to filter.'),
]))
class SymbolViewSet(viewsets.ModelViewSet):
    """View for manage symbol APIs."""

    serializer_class = serializers.SymbolSerializer
    queryset = Symbol.objects.all()

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve symbols for authenticated user."""
        symbols = self.request.query_params.get('symbols')  # type: ignore
        queryset = self.queryset
        # filters
        if symbols:
            symbol_list = symbols.split(',')
            queryset = queryset.filter(name__in=symbol_list)

        return queryset.filter().order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request."""
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save()
