from csv import DictReader
from django.core.management import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    def handle(self, *args, **options):
        for row in DictReader(open('./ingredients.csv')):
            ingredient=Ingredient(name=row['name'], measurement_unit=row['measurement_unit'])
            ingredient.save()
