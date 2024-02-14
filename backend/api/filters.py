from django_filters import FilterSet
from django_filters.filters import (
    BooleanFilter,
    NumberFilter,
    ModelMultipleChoiceFilter,
)
from django_filters.widgets import BooleanWidget

from recipes.models import Recipe, Tag, Ingredient


class RecipeFilter(FilterSet):
    is_favorited = BooleanFilter(
        field_name="is_favorited",
        label='is_favorited',
        widget=BooleanWidget()
    )
    is_in_shopping_cart = BooleanFilter(
        field_name="is_in_shopping_cart",
        label='is_in_shopping_cart',
        widget=BooleanWidget()
    )
    tags = ModelMultipleChoiceFilter(
        field_name='tags__slug',
        queryset=Tag.objects.all(),
        to_field_name='slug',
        conjoined=False,
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')


class IngredientFilter(FilterSet):
    class Meta:
        model = Ingredient
        fields = {
            'name': ['istartswith']
        }
