from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from .models import (Favorite, Follow, Ingredient, AmountIngredient,
                     ShoppingList, Recipe, Tag)

User = get_user_model()


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.
    Минимальный набор полей для определенных эндпоинтов.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели User."""

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
            'password',
        )
        extra_kwargs = {'password': {'write_only': True}}
        read_only_fields = ('is_subscribed',)

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Follow.objects.filter(
            user=request.user,
            author=obj.id).exists()


class UserSubscribeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для вывода авторов на которых подписан
    текущий пользователь.
    """

    id = serializers.ReadOnlyField(source='author.id')
    email = serializers.ReadOnlyField(source='author.email')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        return Follow.objects.filter(
            user=obj.user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        print(queryset)
        return SimpleRecipeSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return Recipe.objects.filter(author=obj.author).count()



class TagSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Tag."""

    class Meta:
        model = Tag
        fields = '__all__'


class TagListField(serializers.RelatedField):
    """ Сериализатор для получения списка тэгов."""

    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'color': obj.color,
            'slug': obj.slug
        }

    def to_internal_value(self, data):
        try:
            return Tag.objects.get(id=data)
        except ObjectDoesNotExist:
            raise serializers.ValidationError(
                'Объект не существует.'
            )


class IngredientSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientsAmountSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели AmountIngredient."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_representation(self, instance):
        data = IngredientSerializer(instance.ingredient).data
        data['amount'] = instance.amount
        return data


class IngredientsAmountReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели AmountIngredient на чтение."""

    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    
    class Meta:
        model = AmountIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_representation(self, instance):
        data = IngredientSerializer(instance).data
        return data


class ListRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения списка рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountReadSerializer(
        many=True,
    )
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'description',
            'cooking_time',
        )
        read_only_fields = ('author', 'tags',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request.user.is_authenticated:
            return ShoppingList.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False


class CreateUpdateRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для создания и обновления рецептов."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'description',
            'cooking_time',
        )

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            AmountIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient["ingredient"],
                amount=ingredient.get('amount'), )
            
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe.name = validated_data.get('name', recipe.name)
        recipe.image = validated_data.get('image', recipe.image)
        recipe.description = validated_data.get('text', recipe.description)
        recipe.cooking_time = validated_data.get(
            'cooking_time',
            recipe.cooking_time
        )
        recipe.save()
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_amount, status = (
                AmountIngredient.objects.get_or_create(**ingredient)
            )
            ingredients_list.append(ingredient_amount)
        recipe.ingredients.set(ingredients_list)
        recipe.tags.set(tags)
        return recipe

    def to_representation(self, obj):
        self.fields.pop('ingredients')
        self.fields['tags'] = TagSerializer(many=True)
        representation = super().to_representation(obj)
        representation['ingredients'] = IngredientsAmountSerializer(
            AmountIngredient.objects.filter(recipe=obj).all(), many=True
        ).data
        return representation    


class FavoritesSerializer(serializers.ModelSerializer):
    """ Сериализатор для избранных рецептов"""

    id = serializers.ReadOnlyField(source='recipe.id')
    name = serializers.ReadOnlyField(source='recipe.name')
    image = Base64ImageField(source='recipe.image', read_only=True)
    cooking_time = serializers.ReadOnlyField(source='recipe.cooking_time')

    class Meta:
        model = Favorite
        fields = ('id', 'name', 'image', 'cooking_time', 'user', 'recipe')
        extra_kwargs = {'user': {'write_only': True},
                        'recipe': {'write_only': True}}

    def validate(self, data):
        if Favorite.objects.filter(user=data['user'],
                                   recipe=data['recipe']).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data


class ShoppingListSerializer(FavoritesSerializer):
    """ Сериализатор для списка покупок"""

    class Meta(FavoritesSerializer.Meta):
        model = ShoppingList

    def validate(self, data):
        request = self.context.get('request')
        recipe_id = data['recipe'].id
        purchase= ShoppingList.objects.filter(
            user=request.user,
            recipe__id=recipe_id
        ).exists()

        if purchase:
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок'
            )
        return data

    def to_representation(self, instance):
        request = self.context.get('request')
        context = {'request': request}
        return SimpleRecipeSerializer(
            instance.recipe,
            context=context).data
