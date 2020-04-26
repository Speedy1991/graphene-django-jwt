from datetime import timedelta

from django.conf import settings
from django.utils.module_loading import import_string

DEFAULTS = {
    'GRAPHENE_JWT_ALGORITHM': 'HS256',
    'GRAPHENE_JWT_SECRET_KEY': settings.SECRET_KEY,
    'GRAPHENE_JWT_EXPIRATION_DELTA': timedelta(seconds=60 * 5),
    'GRAPHENE_JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
    'GRAPHENE_JWT_AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'GRAPHENE_JWT_AUTH_HEADER_PREFIX': 'Bearer',
    'GRAPHENE_JWT_ENCODE_HANDLER': 'django_graphene_jwt.utils.jwt_encode',
    'GRAPHENE_JWT_DECODE_HANDLER': 'django_graphene_jwt.utils.jwt_decode',
    'GRAPHENE_JWT_PAYLOAD_HANDLER': 'django_graphene_jwt.utils.jwt_payload',
    'GRAPHENE_JWT_BLACKLIST_HANDLER': 'django_graphene_jwt.blacklist.DefaultBlacklistHandler',
    'GRAPHENE_JWT_CACHE_PREFIX': 'jwt',
}

IMPORT_STRINGS = (
    'GRAPHENE_JWT_ENCODE_HANDLER',
    'GRAPHENE_JWT_DECODE_HANDLER',
    'GRAPHENE_JWT_PAYLOAD_HANDLER',
    'GRAPHENE_JWT_BLACKLIST_HANDLER',
)


def perform_import(value, setting_name):
    if isinstance(value, str):
        return import_from_string(value, setting_name)
    if isinstance(value, (list, tuple)):
        return [import_from_string(item, setting_name) for item in value]
    return value


def import_from_string(value, setting_name):
    try:
        return import_string(value)
    except ImportError as e:
        msg = 'Could not import `{}` for JWT setting `{}`. {}: {}.'.format(
            value, setting_name, e.__class__.__name__, e,
        )
        raise ImportError(msg)


class GrapheneJWTSettings:
    def __init__(self, defaults, import_strings):
        self.defaults = defaults
        self.import_strings = import_strings
        self._cached_attrs = set()

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid setting: `{}`'.format(attr))

        value = self.user_settings.get(attr, self.defaults[attr])

        if attr in self.import_strings:
            value = perform_import(value, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, value)
        return value

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'GRAPHQL_JWT', {})
        return self._user_settings

    def reload(self):
        for attr in self._cached_attrs:
            delattr(self, attr)

        self._cached_attrs.clear()

        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')


jwt_settings = GrapheneJWTSettings(DEFAULTS, IMPORT_STRINGS)
