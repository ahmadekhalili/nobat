# setup redis-server local
# create .env in root of project:
```
ALLOWED_HOSTS=*
TEST_RESERVATION=True
SECURE_SSL_REDIRECT=False
DRIVER_PATH=your windows or linux path
CHROME_PATH=your windows or linux path
WINDOWS_CRAWL=True (in win) or False (in linux)
REDIS_PASS= (redid db pass if set)
```
# create logs folder with at least 664 perms in root, sudo chmod -R 664 logs/
python manage.py makemigrations
python manage.py migrate

python manage.py init
python manage.py pre_centers
python manage.py centers
python manage.py createsuperuser

