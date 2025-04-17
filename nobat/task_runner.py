import django
import logging
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nobat.settings")
django.setup()


from django.conf import settings


BASE_DIR = settings.BASE_DIR
log_file_path = os.path.join(BASE_DIR, 'logs', f'threads.log')


if __name__ == '__main__':
    print('1111111111', Job)