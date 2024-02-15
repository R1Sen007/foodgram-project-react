from rest_framework import status
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, Prefetch, Sum
from django_filters.rest_framework import DjangoFilterBackend

from api.serializers import (
    UserSerializer,
    CreateUserSerializer,
    TagSerializer,
    RecipeSerializer,
    CreateRecipeSerializer,
    IngredientSerializer,
    ShoppingCardSerializer,
    FavoriteSerializer,
    FollowSerializer,
    CreateFollowSerializer,
    ChangePasswordSerializer,
)
from api.utils import (
    AnnotateMixin,
    create_textfile,
    validate_before_delete,
)
from api.filters import (
    RecipeFilter,
    IngredientFilter,
)
from api.permissions import (
    IsOwnerOrIsAuthenticatedOrReadOnly,
)
from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    ShoppingCard,
    Favorite,
    Follow,
    User,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


class RecipeViewSet(ModelViewSet, AnnotateMixin):
    http_method_names = ['get', 'post', 'patch', 'delete']
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsOwnerOrIsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        author_queryset = self.annotate_qs_is_subscribe_field(
            User.objects.all()
        )
        queryset = (
            super().get_queryset()
                   .prefetch_related(
                       Prefetch('author', queryset=author_queryset),
                       Prefetch('ingredients',
                                queryset=Ingredient.objects.all()),
                       Prefetch('tags', queryset=Tag.objects.all()),)
        )
        queryset = self.annotate_qs_is_favorited_field(queryset)
        queryset = self.annotate_qs_is_in_shopping_cart_field(queryset)

        if self.action == 'download_shopping_cart':
            queryset = (
                queryset.filter(is_in_shopping_cart=True)
                        .only('ingredients')
                        .values('ingredients__name',
                                'ingredients__measurement_unit')
                        .order_by('ingredients__name')
                        .annotate(amount=Sum('recipeingredient__amount'))
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = RecipeSerializer(
            self.get_queryset().get(id=serializer.data['id'])
        ).data
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}
        data = RecipeSerializer(
            self.get_queryset().get(id=serializer.data['id'])
        ).data
        return Response(data)

    @action(
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        ingredients_dict = self.get_queryset()
        return create_textfile(request, ingredients_dict)

    @action(
        detail=True,
        url_path='shopping_cart',
        methods=['post'],
        serializer_class=ShoppingCardSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        shopping_card = validate_before_delete(request.user, ShoppingCard, pk)
        shopping_card.delete()
        return Response(data={'message': 'DELETED'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        url_path='favorite',
        methods=['post'],
        serializer_class=FavoriteSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        favorite = validate_before_delete(request.user, Favorite, pk)
        favorite.delete()
        return Response(data={'message': 'DELETED'},
                        status=status.HTTP_204_NO_CONTENT)


class UserViewSet(ModelViewSet, AnnotateMixin):
    http_method_names = ['get', 'post', 'delete']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        queryset = self.annotate_qs_is_subscribe_field(super().get_queryset())

        if self.action == 'subscriptions':
            queryset = (
                queryset.filter(is_subscribed=True)
                        .prefetch_related('recipes')
                        .annotate(recipes_count=Count('recipes'))
            )
            return queryset

        if self.action in ['subscribe', 'post_subscribe']:
            queryset = (
                queryset.prefetch_related('recipes')
                        .annotate(recipes_count=Count('recipes'))
            )
            return queryset

        return queryset

    def get_serializer_class(self):
        if self.action in ('create',):
            return CreateUserSerializer
        return super().get_serializer_class()

    def destroy(self, request, pk=None):
        pass

    @action(
        detail=False,
        url_path='set_password',
        methods=['post'],
        serializer_class=ChangePasswordSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        current_user = request.user
        new_password = serializer.data.get('new_password')
        current_user.set_password(new_password)
        current_user.save()
        update_session_auth_hash(request, current_user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        url_path='subscriptions',
        methods=['get'],
        serializer_class=FollowSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscriptions(self, request):
        subscriptions = self.get_queryset()
        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(subscriptions, many=True)
        return Response(serializer.data)

    @action(
        detail=True,
        url_path='subscribe',
        methods=['post'],
        serializer_class=CreateFollowSerializer,
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, pk):
        # instance = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            FollowSerializer(
                self.get_object(),
                context=serializer.context
            ).data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk):
        instance = self.get_object()
        try:
            follow_obj = Follow.objects.get(
                user=request.user,
                following=instance
            )
        except Follow.DoesNotExist:
            raise ValidationError(
                f'Данная подписка отстуствует в {Follow.__name__}!'
            )
        follow_obj.delete()
        return Response(data={'message': 'SUBSCRIBE DELETED'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        current_user = request.user
        serializer = self.get_serializer(self.get_queryset()
                                         .get(username=current_user))
        return Response(serializer.data, status=status.HTTP_200_OK)
