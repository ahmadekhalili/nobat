# Project Setup Instructions

## 1. Start Redis Server  
Ensure `redis-server` is running locally.

## 2. Create a `.env` File in the Project Root  
```ini
ALLOWED_HOSTS=*
TEST_RESERVATION=True  # if be True, last submit button will not be pressed (used for test environments)
SECURE_SSL_REDIRECT=False  # False in test environments without ssl domain
DRIVER_PATH=/path/to/driver
CHROME_PATH=/path/to/chrome
CHROME_PROFILE_PATH=
CHROME_PROFILE_FOLDER=
EXTENSION_PATH=
WINDOWS_CRAWL=True  # Set to False on Linux
REDIS_PASS=         # Redis password if set
POSTGRES_DBNAME=
POSTGRES_USERNAME=
POSTGRES_USERPASS=
POSTGRES_DBNAME_CHANEL=
POSTGRES_USERNAME_CHANEL=
POSTGRES_USERPASS_CHANEL=
```

## 3. Set Up Logging Directory and  log files

Create a logs/ directory with appropriate permissions:
```sh
mkdir logs
touch logs/threads.log logs/web.log
sudo chmod -R 664 logs/
```

## 4. Apply Migrations and Initialize Data
```
python manage.py makemigrations
python manage.py migrate
python manage.py init
python manage.py pre_centers
python manage.py centers
python manage.py createsuperuser
```
