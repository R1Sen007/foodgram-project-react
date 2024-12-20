from django.core.management.base import BaseCommand

from recipes.models import (
    Ingredient,
)
from recipes.management.utils import import_simple_csv


class Command(BaseCommand):
    help = 'Импорт CSV data'

    def handle(self, *args, **options):
        import_simple_csv('ingredients.csv', Ingredient)
        print('Все ингредиенты были успешно импрортированы.')
