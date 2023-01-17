from django.contrib.auth import get_user_model
from django.db.models.aggregates import Sum
from django.http.response import HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from recipes.models import (AmountIngredient, Favorite, Ingredient,
                            Recipe, ShoppingList, Tag)

from .filters import IngredientNameFilter, RecipeFilter
from .paginators import PageLimitPagination
from .permissions import OwnerOrAdminOrReadOnly
from .serializers import (CreateUpdateRecipeSerializer, FavoritesSerializer,
                          IngredientSerializer, ListRecipeSerializer,
                          ShoppingListSerializer, TagSerializer)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filterset_class = IngredientNameFilter
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    pagination_class = PageLimitPagination
    permission_classes = (OwnerOrAdminOrReadOnly,)
    filterset_class = RecipeFilter
    serializer_classes = {
        'list': ListRecipeSerializer,
        'retrieve': CreateUpdateRecipeSerializer,
    }
    default_serializer_class = CreateUpdateRecipeSerializer

    def get_serializer_class(self):
        return self.serializer_classes.get(
            self.action,
            self.default_serializer_class
        )

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

    def _recipe_post_method(self, request, AnySerializer, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        data = {
            'user': user.id,
            'recipe': recipe.id,
        }
        serializer = AnySerializer(
            data=data,
            context={'request': request}
        )
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _recipe_delete_method(self, request, AnyModel, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        favorites = get_object_or_404(
            AnyModel, user=user, recipe=recipe
        )
        favorites.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self.recipe_post_method(
                request, FavoritesSerializer, pk
            )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self.recipe_delete_method(
            request, Favorite, pk
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self.recipe_post_method(
                request, ShoppingListSerializer, pk
            )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self.recipe_delete_method(
            request, ShoppingList, pk
        )

    @action(detail=False, methods=['get',],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = self.request.user
        queryset = self.get_queryset()
        carts = ShoppingList.objects.filter(user=request.user)
        recipes = queryset.filter(purchases__in=carts)
        ingredients = AmountIngredient.objects.filter(recipe__in=recipes)
        ing_types = Ingredient.objects.filter(
            ingredients_amount__in=ingredients
        ).annotate(total=Sum('ingredients_amount__amount'))

        lines = [f'{ing_type.name}, {ing_type.total}'
                 f' {ing_type.measurement_unit}' for ing_type in ing_types]
        filename = f'{user.username}_shopping_list.txt'
        response_content = '\n'.join(lines)
        response = HttpResponse(response_content, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
