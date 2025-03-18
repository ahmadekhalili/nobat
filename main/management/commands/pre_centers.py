from django.core.management.base import BaseCommand

import json

from user.models import Town, Center


class Command(BaseCommand):
    help = 'create pre centers (centers without services)'

    def handle(self, *args, **options):
        with open('pre_centers.json', 'r', encoding='utf-8') as f:
            centers_obj = json.load(f)
            for center_obj in centers_obj:
                for center in center_obj['centers']:
                    if Center.objects.filter(title=center['title']).exists():
                        center_model = Center.objects.get(title=center['title'])
                        center_model.towns.add(Town.objects.get(name=center_obj['town']))
                    else:
                        if center['code']:
                            center_model = Center.objects.create(title=center['title'], address=center['address'], code=center['code'], active=True)
                        else:  # centers with code=None are inactive
                            center_model = Center.objects.create(title=center['title'], address=center['address'], code='', active=False)
                        center_model.towns.add(Town.objects.get(name=center_obj['town']))
        self.stdout.write(self.style.SUCCESS('Successfully created all pre center locations'))


