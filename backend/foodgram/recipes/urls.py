from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import IngredientsViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'recipes'

router = DefaultRouter()

router.register('users', UserViewSet, 'users')
router.register('recipes', RecipeViewSet, 'recipes')
router.register('tags', TagViewSet, 'tags')
router.register('ingredients', IngredientsViewSet, 'ingredients')

urlpatterns = [
    path('', include(router.urls)),
]
