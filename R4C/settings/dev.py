from .common import *

SECRET_KEY = 'mztx@x_-=gfhc9xs@bm58m&@3pc7##opo14zob!(l2tus05+jo'

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "r4c_db",
        "USER": "postgres",
        "PASSWORD": "password",
        "HOST": "db",
        "PORT": "5432",
    }
}