from datetime import timedelta

SECRET_KEY = 'test'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'graphene_django',
    'graphene_django_jwt',
    'tests',
]

GRAPHENE = {
    'SCHEMA': 'tests.schema.schema',
    'SCHEMA_INDENT': 2,
    'MIDDLEWARE': [
        'graphene_django_jwt.schema.middleware.JSONWebTokenMiddleware',
    ],
}

ROOT_URLCONF = 'tests.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

GRAPHENE_JWT_EXPIRATION_DELTA = timedelta(seconds=3)
GRAPHENE_JWT_REFRESH_EXPIRATION_DELTA = timedelta(seconds=10)
