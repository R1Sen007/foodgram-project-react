import csv

from django.conf import settings


def import_simple_csv(filename, model):
    csv_file = settings.CSV_FILES / filename

    with open(csv_file, 'r') as f:
        csv_dict = csv.DictReader(f)
        instances_list = []
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
            instances_list.append(model_instance)
        model.objects.bulk_create(instances_list)
