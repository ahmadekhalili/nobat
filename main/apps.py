from django.apps import AppConfig


class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):      # create just once OpenedBrowser in all live cycle of program in robust way
        pass
        """
        try:
            from main.models import OpenedBrowser
            if not OpenedBrowser.objects.exists():
                OpenedBrowser.objects.create()
        except:
            # Happens when DB or table doesn't exist yet (e.g. during migrate)
            pass
        """