from django.db.utils import IntegrityError
from django.contrib.auth.password_validation import validate_password
from rest_framework.serializers import (
    Serializer,
    ModelSerializer,
    CurrentUserDefault,
    ValidationError,
    SerializerMethodField,
    HiddenField,
    ReadOnlyField,
    IntegerField,
    BooleanField,
    CharField,
)
from rest_framework.validators import UniqueTogetherValidator
from drf_base64.fields import Base64ImageField

from recipes.models import (
    Tag,
    Ingredient,
    Recipe,
    Follow,
    Favorite,
    ShoppingCard,
    RecipeIngredient,
    User,
)
from api.utils import (
    CurrentRecipeDefault,
    CurrentFollowingUserDefault,
    DynamicFieldsModelSerializer,
)


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('id', 'name', 'color', 'slug')


class UserBaseSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name')


class UserSerializer(UserBaseSerializer):
    is_subscribed = BooleanField(read_only=True)

    class Meta(UserBaseSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed')


class CreateUserSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(Serializer):
    new_password = CharField(
        validators=[
            validate_password,
        ]
    )
    current_password = CharField()

    def validate_current_password(self, value):
        current_user = self.context['request'].user
        if not current_user.check_password(value):
            raise ValidationError('Incorrect current password!')
        return value


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientSerializer(ModelSerializer):
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    measurement_unit = ReadOnlyField(source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class ChooseRecipeIngredientSerializer(ModelSerializer):
    id = IntegerField(source='ingredient.id')
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeSerializer(DynamicFieldsModelSerializer):
    is_favorited = BooleanField(read_only=True)
    is_in_shopping_cart = BooleanField(read_only=True)
    ingredients = RecipeIngredientSerializer(
        source='recipeingredient_set',
        many=True,
    )
    image = SerializerMethodField('get_image_url')
    tags = TagSerializer(many=True)
    author = UserSerializer()

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class CreateRecipeSerializer(ModelSerializer):
    ingredients = ChooseRecipeIngredientSerializer(
        many=True,
        source='recipeingredient_set',
    )
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time')

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError({
                'ingredients': 'Нужен хотя бы один ингредиент!'
            })
        for item in ingredients:
            if int(item['amount']) <= 0:
                raise ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0!'
                })
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError({'tags': 'Нужно выбрать хотя бы один тег!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Теги должны быть уникальными!'}
                )
            tags_list.append(tag)
        return value

    def create_recipeingredients(self, ingredients, recipe):
        try:
            RecipeIngredient.objects.bulk_create(
                [RecipeIngredient(
                    ingredient=Ingredient.objects.get(
                        **ingredient['ingredient']
                    ),
                    recipe=recipe,
                    amount=ingredient['amount']
                ) for ingredient in ingredients]
            )
        except IntegrityError:
            raise ValidationError({
                'ingredients': 'Ингридиенты не могут повторяться!'
            })
        except Ingredient.DoesNotExist:
            raise ValidationError({
                'ingredients': 'Неопознанный ингредиент!'
            })

    def create(self, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')

        validated_data['author'] = self.context['request'].user
        recipe = super().create(validated_data)

        self.create_recipeingredients(ingredients_data, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('recipeingredient_set')
        instance = super().update(instance, validated_data)
        instance.ingredients.clear()
        self.create_recipeingredients(ingredients_data, instance)
        instance.save()
        return instance


class ShoppingCardSerializer(Serializer):
    user = HiddenField(default=CurrentUserDefault())
    recipe = HiddenField(default=CurrentRecipeDefault())

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=ShoppingCard.objects.all(),
                fields=('user', 'recipe')
            ),
        ]

    def create(self, validated_data):
        return ShoppingCard.objects.create(**validated_data)

    def to_representation(self, instance):
        recipe = (instance.recipe if isinstance(instance, ShoppingCard)
                  else instance['recipe'])
        fields = ('id', 'name', 'image', 'cooking_time')
        return RecipeSerializer(recipe, fields=fields).data


class FavoriteSerializer(ShoppingCardSerializer):

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe')
            ),
        ]

    def create(self, validated_data):
        return Favorite.objects.create(**validated_data)

    def to_representation(self, instance):
        recipe = (instance.recipe if isinstance(instance, Favorite)
                  else instance['recipe'])
        fields = ('id', 'name', 'image', 'cooking_time')
        return RecipeSerializer(recipe, fields=fields).data


class FollowSerializer(UserSerializer):
    recipes = SerializerMethodField()
    recipes_count = IntegerField()

    class Meta(UserSerializer.Meta):
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_recipes(self, obj):
        recipes_qs = obj.recipes.all()
        recipes_limit = (self.context['request']
                             .query_params.get('recipes_limit'))
        if recipes_limit is not None:
            recipes_qs = recipes_qs[:int(recipes_limit)]
        return RecipeSerializer(
            recipes_qs,
            fields=('id', 'name', 'image', 'cooking_time'),
            many=True
        ).data


class CreateFollowSerializer(Serializer):
    user = HiddenField(default=CurrentUserDefault())
    following = HiddenField(default=CurrentFollowingUserDefault())

    class Meta:
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'following')
            ),
        ]

    def validate(self, data):
        user = self.context.get('request').user
        if user == data['following']:
            raise ValidationError(
                'Вы не можете подписаться на самого себя!'
            )
        return data

    def create(self, validated_data):
        return Follow.objects.create(**validated_data)

    def to_representation(self, instance):
        return FollowSerializer(instance.following, context=self.context).data
