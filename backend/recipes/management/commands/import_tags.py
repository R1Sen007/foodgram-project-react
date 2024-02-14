from django.core.management.base import BaseCommand

from recipes.models import (
    Tag,
)
from recipes.management.utils import import_simple_csv


class Command(BaseCommand):
    help = 'Импорт CSV data'

    def handle(self, *args, **options):
        import_simple_csv('tags.csv', Tag)
        print('Все теги были успешно импрортированы.')
