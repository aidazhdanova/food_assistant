from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (IngredientsViewSet, TagsViewSet,
                    RecipeViewSet, UserViewSet)

app_name = 'api'

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet)
router.register('tags', TagsViewSet)
router.register('recipes', RecipeViewSet)
router.register('users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]