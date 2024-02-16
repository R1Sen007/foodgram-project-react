from django.shortcuts import get_object_or_404
from django.db.models import Exists, OuterRef, Value
from django.http import HttpResponse
from rest_framework.serializers import ModelSerializer, ValidationError


from recipes.models import (
    Recipe,
    Follow,
    Favorite,
    ShoppingCard,
    User,
)


class CurrentRecipeDefault:
    requires_context = True

    def __call__(self, serializer_field):
        pk = serializer_field.context[
            'request'].resolver_match.kwargs.get('pk')
        try:
            return Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            raise ValidationError(
                'Неопознанный рецепт!'
            )


class CurrentFollowingUserDefault:
    requires_context = True

    def __call__(self, serializer_field):
        pk = serializer_field.context[
            'request'].resolver_match.kwargs.get('pk')
        instance = get_object_or_404(User, pk=pk)
        return instance


class AnnotateMixin:
    def annotate_qs_is_subscribe_field(self, queryset, outerRef='pk'):
        if self.request.user.is_authenticated:
            is_subscribed = Follow.objects.filter(
                user=self.request.user,
                following=OuterRef(outerRef)
            )
            queryset = queryset.annotate(is_subscribed=Exists(is_subscribed))
        else:
            queryset = queryset.annotate(is_subscribed=Value(False))
        return queryset

    def annotate_qs_is_favorited_field(self, queryset, outerRef='pk'):
        if self.request.user.is_authenticated:
            is_favorited = Favorite.objects.filter(
                user=self.request.user,
                recipe=OuterRef(outerRef)
            )
            queryset = queryset.annotate(is_favorited=Exists(is_favorited))
        else:
            queryset = queryset.annotate(is_favorited=Value(False))
        return queryset

    def annotate_qs_is_in_shopping_cart_field(self, queryset, outerRef='pk'):
        if self.request.user.is_authenticated:
            is_in_shopping_cart = ShoppingCard.objects.filter(
                user=self.request.user,
                recipe=OuterRef(outerRef)
            )
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(is_in_shopping_cart)
            )
        else:
            queryset = queryset.annotate(
                is_in_shopping_cart=Value(False)
            )
        return queryset


class DynamicFieldsModelSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)
        super().__init__(*args, **kwargs)
        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


def create_textfile(request, ingredients):
    text = (
        'Ваш список покупок:\n'
    )
    for ingredient in ingredients:
        text += (
            f'{ingredient["ingredients__name"]}: '
            f'{ingredient["amount"]} '
            f'{ingredient["ingredients__measurement_unit"]}\n'
        )
    # response = FileResponse(text, as_attachment=True)
    response = HttpResponse(text, content_type='text/plain')
    response['Content-Disposition'] = (
        u'attachment; filename="shoppinglist.txt"'
    )
    return response


def validate_before_delete(current_user, model, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    try:
        model_object = model.objects.get(user=current_user, recipe=recipe)
    except model.DoesNotExist:
        raise ValidationError(
            f'Данный рецепт отстуствует в {model.__name__}!'
        )
    return model_object
