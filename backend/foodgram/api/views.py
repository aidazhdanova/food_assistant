from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientSearchFilter, RecipeFilter
from .pagination import PageLimitPagination
from .permissions import AdminOrReadOnly, AdminUserOrReadOnly
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeCreateSerializer, RecipeSerializer,
                          ShoppingCartSerializer, SubscriptionSerializer,
                          TagSerializer)
from recipes.models import (Favourite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscribe, User


class TagsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (AdminOrReadOnly,)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientSearchFilter
    search_fields = ('name__startswith',)


class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (AdminUserOrReadOnly,)
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageLimitPagination

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    @staticmethod
    def post_method(request, pk, serializers):
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method(request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        model_obj = get_object_or_404(model, user=user, recipe=recipe)
        model_obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk):
        return self.post_method(
            request=request, pk=pk, serializers=FavoriteSerializer)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk):
        return self.delete_method(
            request=request, pk=pk, model=Favourite)

    @action(detail=True, methods=["POST"],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk):
        self.queryset = self.queryset.prefetch_related('shopping')
        return self.post_method(
            request=request, pk=pk, serializers=ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk):
        return self.delete_method(
            request=request, pk=pk, model=ShoppingCart)

    @action(detail=False, methods=['GET'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).order_by('ingredient__name').annotate(total=Sum('amount'))

        content = ''
        for ingredient in ingredients:
            ingredient_name = ingredient['ingredient__name']
            total_amount = ingredient['total']
            measurement_unit = ingredient['ingredient__measurement_unit']
            line = f'{ingredient_name} ({measurement_unit}) — {total_amount}\n'
            content += line

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename=shopping_cart.txt'

        return response


class CustomUserViewSet(UserViewSet):
    pagination_class = PageLimitPagination
    ''' Я понимаю, что нужно было просто убрать ветку с elif, но решила переписать код
    Сейчас вроде как все должно быть корректно. '''

    @staticmethod
    def post_method(request, id, serializers):
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response({
                'errors': 'Подписаться на себя не получится!'},
                status=status.HTTP_400_BAD_REQUEST)
        if Subscribe.objects.filter(user=user, author=author).exists():
            return Response({
                'errors': 'Вы уже подписаны на этого пользователя!'},
                status=status.HTTP_400_BAD_REQUEST)

        follow = Subscribe.objects.create(user=user, author=author)
        serializer = serializers(
            follow, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method(request, id):
        subscriber = request.user
        author = get_object_or_404(User, id=id)
        subscription = Subscribe.objects.filter(
            user=subscriber, author=author)
        if not subscription.exists():
            return Response(
                {'errors': 'Такой подписки нет!'},
                status=status.HTTP_400_BAD_REQUEST)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST'],
            detail=True,
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        return self.post_method(
            request=request, id=id, serializers=SubscriptionSerializer)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        return self.delete_method(request=request, id=id)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        if pages is not None:
            serializer = SubscriptionSerializer(
                pages, many=True,
                context={'request': request}
            )
            return self.get_paginated_response(serializer.data)
        raise NotFound()
