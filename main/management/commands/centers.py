from django.core.management.base import BaseCommand

import json
import warnings

from user.models import *
from main.models import *


class Command(BaseCommand):
    help = 'create pre centers (centers without services)'

    def handle(self, *args, **options):
        with open('services.json', 'r', encoding='utf-8') as f:
            centers_obj = json.load(f)
            for center_obj in centers_obj:
                for service in center_obj['services']:
                    if ServiceType.objects.filter(name=service).exists():
                        center_model = Center.objects.get(title=center_obj['title'])
                        center_model.services.add(ServiceType.objects.get(name=service))
                    else:
                        self.stdout.write(self.style.WARNING(f'Service {service} not founded!'))
        self.stdout.write(self.style.SUCCESS('Successfully created all finalized centers'))
