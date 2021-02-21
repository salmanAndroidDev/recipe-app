from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from . import serializers


class BaseTagIngredientViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.CreateModelMixin):
    """Base class for ingredient and tag with common functionalities"""
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """get objects belong to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        """Create a new object with authenticated user"""
        serializer.save(user=self.request.user)


class TagViewSet(BaseTagIngredientViewSet):
    """Manage Tag """
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewSet(BaseTagIngredientViewSet):
    """Manage Ingredient"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
