from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from recipes.constants import (
    MAX_TEXT_LENGTH,
    MAX_NAME_LENGTH,
    SHORT_VIEW_LENGTH,
)

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название тега'
    )
    color = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        unique=True
    )

    class Meta:
        # ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:SHORT_VIEW_LENGTH]


class Ingredient(models.Model):
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Единица измерения'
    )

    class Meta:
        # ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient',
            )
        ]

    def __str__(self):
        return self.name[:SHORT_VIEW_LENGTH]


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        max_length=MAX_NAME_LENGTH,
        verbose_name='Название рецепта'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    text = models.TextField(
        max_length=MAX_TEXT_LENGTH,
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes'
        )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Тэг'
    )
    cooking_time = models.IntegerField(
        # validator min value 1
        validators=[
            MinValueValidator(1, 'Cooking_time can`t be less 1.'),
        ],
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return str(self.name)[:SHORT_VIEW_LENGTH]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(1, 'Amount can`t be less 1.'),]
    )

    class Meta:
        # ordering = ('name',)
        verbose_name = 'Рецепт & Ингредиент'
        verbose_name_plural = 'Рецепты & Ингредиенты'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipeingredient'
            )
        ]

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='follows'
    )
    following = models.ForeignKey(
        User, on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_user_following'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.following}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное пользователей'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCard(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_possitions'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopcard_user_recipe'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'
