from django.core.management.base import BaseCommand

from main.states_towns import list_states_towns
from user.models import ServiceType, State, Town


class Command(BaseCommand):
    help = 'create states and its towns'
    services_text = ['نقل و انتقال', 'خدمات کارت وسیله نقلیه(المثنی/عودتی)', 'پلاک المثنی',
                     'تغییر کد پلاک مالک (از شهری به شهر دیگر)', 'خدمات جانبازان و معلولین',
                     'تعویض ارکان(اتاق، شاسی، موتور و رنگ) وسیله نقلیه', 'سند مالکیت المثنی', 'اصلاح مشخصات', 'فک رهن',
                     'پلاک مجازی', 'مزایده ای', 'نوشماره (تولید داخل / وارداتی)', 'نصب پلاک / فک پلاک گذر موقت',
                     'تعویض پلاک سرقتی / پلاک مفقودی']

    def handle(self, *args, **options):
        towns = []
        for L in list_states_towns:
            state = State(name=L[0])
            state.save()
            for town in L[1]:
                towns.append(Town(name=town, state_id=state.id))

        Town.objects.bulk_create(towns)

        services_obj = []
        for service in self.services_text:
            services_obj.append(ServiceType(name=service))
        ServiceType.objects.bulk_create(services_obj)
        self.stdout.write(self.style.SUCCESS(f'Successfully created all {len(list_states_towns)} states and its towns.\n'
                                             f'Successfully created all pre definded services'))



