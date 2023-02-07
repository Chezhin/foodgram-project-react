from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import AmountIngredient, Favorite, Follow, Ingredient, Recipe, Tag


class AmountIngredientInline(admin.TabularInline):
    model = AmountIngredient
    can_delete = False
    autocomplete_fields = ['ingredient']
    extra = 1


@admin.register(Ingredient)
class IngredientAdmin(ImportExportModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name', 'favorited')
    filter_horizontal = ('tags',)
    list_filter = ('author', 'name', 'tags')
    inlines = (AmountIngredientInline,)

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorited.short_description = 'В избранном'


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')


class AmountIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(AmountIngredient, AmountIngredientAdmin)
admin.site.register(Follow)
