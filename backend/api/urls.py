from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    TagViewSet,
    IngredientViewSet,
    RecipeViewSet,
    UserViewSet,
)


router = DefaultRouter()

router.register('tags', TagViewSet, basename='tag')
router.register('ingredients', IngredientViewSet, basename='ingredient')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('users', UserViewSet, basename='user')


urlpatterns = [
    # path('v1/', include(router.urls)),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    # path('v1/', include('djoser.urls.jwt')),
]
