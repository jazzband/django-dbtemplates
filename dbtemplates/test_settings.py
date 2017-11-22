DBTEMPLATES_CACHE_BACKEND = 'dummy://'

DATABASE_ENGINE = 'sqlite3'
# SQLite does not support removing unique constraints (see #28)
SOUTH_TESTS_MIGRATE = False

SITE_ID = 1

SECRET_KEY = 'something-something'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'dbtemplates',
]

MIDDLEWARE_CLASSES = (
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'dbtemplates.loader.Loader',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'loaders': TEMPLATE_LOADERS,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
            ]
        }
    },
]
