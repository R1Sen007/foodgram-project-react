import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from recipes.models import (
    Ingredient,
)


User = get_user_model()


class Command(BaseCommand):
    help = 'Импорт CSV data'

    def handle(self, *args, **options):
        self.import_simple_csv('ingredients.csv', Ingredient)
        print('Все файлы были успешно импрортированы.')

    def import_simple_csv(self, filename, model):
        csv_file = settings.CSV_FILES / filename

        with open(csv_file, 'r') as f:
            csv_dict = csv.DictReader(f)
            for row in csv_dict:
                model_instance = model()
                for attr in csv_dict.fieldnames:
                    model_field = model._meta.get_field(attr)
                    if not model_field.is_relation:
                        setattr(model_instance, attr, row.get(attr))
                    else:
                        setattr(
                            model_instance,
                            attr,
                            model_field.related_model.objects.get(
                                id=row.get(attr)
                            )
                        )
                model_instance.save()
