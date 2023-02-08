from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from recipes.models import (AmountIngredient, Favorite, Ingredient, Recipe,
                            ShoppingList, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer

User = get_user_model()


class SimpleRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Recipe.
    Минимальный набор полей для определенных эндпоинтов.
    """

    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


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
        tag = get_object_or_404(Tag, id=data)
        return tag


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


class IngredientsAmountReadSerializer(serializers.ModelSerializer):
    """ Сериализатор для модели AmountIngredient на чтение."""

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
        data = IngredientSerializer(instance).data
        return data


class ListRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор для получения списка рецептов."""

    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountReadSerializer(
        many=True,
    )
    image = Base64ImageField(max_length=None, use_url=True)
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
            'text',
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
    """ Сериализатор для создания, получения и обновления рецепта."""

    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all())
    image = Base64ImageField(max_length=None, use_url=True)
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
            'text',
            'cooking_time',
        )

    def validate(self, data):
        list_ingr = [item['ingredient'] for item in data['ingredients']]
        all_ingredients, distinct_ingredients = (
            len(list_ingr), len(set(list_ingr)))

        if all_ingredients != distinct_ingredients:
            raise serializers.ValidationError(
                {'error': 'Ингредиенты должны быть уникальными'}
            )
        return data

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

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            AmountIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient["ingredient"],
                amount=ingredient.get('amount'), )
            
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        text = validated_data.pop('text')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(image=image, text=text, **validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        instance.tags.set(tags)
        self.create_ingredients(ingredients, instance)
        instance.save()
        return super().update(instance, validated_data)


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
    image = Base64ImageField(read_only=True)
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
