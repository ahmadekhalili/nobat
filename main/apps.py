from django.apps import AppConfig
from django.db.models.signals import post_migrate


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):      # create just once OpenedBrowser in all live cycle of program in robust way
        from .models import OpenedBrowser

        def ensure_openedbrowser(sender, **kwargs):  # create OpenedBrowser only one in totall program works cycle
            # idempotent
            try:
                obj, created = OpenedBrowser.objects.get_or_create(pk=1)
                if created:
                    print("🟢 OpenedBrowser instance created (pk=%s).", obj.pk)
            except Exception as e:
                print("❌ Could not create OpenedBrowser instance: %s", e)
        post_migrate.connect(ensure_openedbrowser, sender=self)