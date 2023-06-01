from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import PageLimitPagination
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeSerializer, ShortRecipeSerializer,
                             SubscriptionSerializer, TagSerializer)
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipes.models import Favourite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response
from users.models import Subscribe, User

from .permissions import AdminOrReadOnly, AdminUserOrReadOnly


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter
    search_fields = ('^name',)
    filterset_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminUserOrReadOnly | AdminOrReadOnly,)
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination


    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer
    
    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        if request.method == 'POST':
            return self.add_to(Favourite, request.user, pk)
        else:
            return self.delete_from(Favourite, request.user, pk)


    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        return self.toggle_relation(ShoppingCart, request, pk)

    def toggle_relation(self, model, request, pk=None):
        user = request.user
        recipe = self.get_object()

        if model.objects.filter(user=user, recipe=recipe).exists():
            model.objects.filter(user=user, recipe=recipe).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            model.objects.create(user=user, recipe=recipe)
            serializer = ShortRecipeSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class UserViewSet(UserViewSet):

    @action(detail=False, permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user = request.user
        author = get_object_or_404(User, id=id)

        if user == author:
            return Response({
                'errors': 'Подписаться на себя не получится.'},
                status=status.HTTP_400_BAD_REQUEST)
        if Subscribe.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST)

        follow = Subscribe.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            pages, many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def delete_subscribe(self, request, id=None):
        subscriber = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            subscriber=subscriber, author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Такой подписки нет.'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
