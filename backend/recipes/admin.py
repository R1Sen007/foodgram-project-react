from django.contrib import admin
from django.db.models import Count

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    RecipeIngredient,
    Follow,
    Favorite,
    ShoppingCard,
)
from recipes.constants import (
    SHORT_VIEW_LENGTH,
)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Tag info."""

    list_display = ['id', 'name', 'color']


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Ingredient info."""

    list_display = ['id', 'name', 'measurement_unit']
    list_filter = ['name']


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Recipe info."""

    inlines = [RecipeIngredientInline, ]
    list_display = ['id', 'author', 'name', 'get_text',
                    'cooking_time', 'favorited']
    list_filter = ['name', 'author', 'tags']

    def get_text(self, obj):
        return obj.text[:SHORT_VIEW_LENGTH]

    get_text.short_description = 'text'

    def favorited(self, obj):
        querry = (
            Favorite.objects
                    .filter(recipe=obj).aggregate(count=Count("user"))
        )
        return querry['count']

    favorited.short_description = "Кол-во избранных"


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    """RecipeIngredient info."""

    list_display = ['recipe', 'ingredient', 'amount']
    list_filter = ['ingredient']


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Follow info."""


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Favorite info."""


@admin.register(ShoppingCard)
class ShoppingCardAdmin(admin.ModelAdmin):
    """ShoppingCard info."""
