from django.contrib.auth import get_user_model
from djoser.conf import settings
from djoser.serializers import (SetPasswordSerializer, UserCreateSerializer,
                                UserSerializer)
from drf_extra_fields.fields import Base64ImageField
from recipes.models import Follow, Recipe
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj.id).exists()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = tuple(User.REQUIRED_FIELDS) + (
            User.USERNAME_FIELD,
            'password',
        )


class CustomUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = (settings.LOGIN_FIELD, settings.USER_ID_FIELD
                  ) + tuple(User.REQUIRED_FIELDS)
        read_only_fields = (settings.LOGIN_FIELD,)


class CustomSetPasswordSerializer(SetPasswordSerializer):
    class Meta:
        fields = ('password',)


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.
    Минимальный набор полей для определенных эндпоинтов.
    """

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSubscribeSerializer(UserSerializer):
    """
    Сериализатор для вывода авторов на которых подписан
    текущий пользователь.
    """

    recipes = SimpleRecipeSerializer(many=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes_count(self, obj):
        return obj.recipes.count()
