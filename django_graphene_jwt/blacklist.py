from django.core.cache import cache
from django.utils import timezone

from django_graphene_jwt.settings import jwt_settings

JWT_BLACKLIST_KEY = f"{jwt_settings.GRAPHENE_JWT_CACHE_PREFIX}'/blacklist/%s"


class DefaultBlacklistHandler:

    @classmethod
    def set(cls, refresh_token_obj):
        key = JWT_BLACKLIST_KEY % refresh_token_obj.token
        expire = timezone.now() - refresh_token_obj.created
        expire += jwt_settings.GRAPHENE_JWT_REFRESH_EXPIRATION_DELTA
        # Add 10 seconds - just to be sure
        expire = int(expire.total_seconds()) + 10
        cache.set(key, expire)

    @classmethod
    def is_blacklisted(cls, refresh_token):
        key = JWT_BLACKLIST_KEY % refresh_token
        return cache.get(key, default=False)


Blacklist = jwt_settings.GRAPHENE_JWT_BLACKLIST_HANDLER
