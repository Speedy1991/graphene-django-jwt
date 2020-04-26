from calendar import timegm
from datetime import datetime

from django.contrib.auth import get_user_model
from django.utils.translation import ugettext as _

import jwt

from django_graphene_jwt.exceptions import JSONWebTokenError, JSONWebTokenExpired
from django_graphene_jwt.settings import jwt_settings

UserModel = get_user_model()


def jwt_payload(user, **kwargs):
    payload = {
        'id': str(user.id),
        'exp': datetime.utcnow() + jwt_settings.GRAPHENE_JWT_EXPIRATION_DELTA,
        'origIat': timegm(datetime.utcnow().utctimetuple()),
        **kwargs,
    }

    return payload


def jwt_encode(payload):
    return jwt.encode(
        payload,
        jwt_settings.GRAPHENE_JWT_SECRET_KEY,
        jwt_settings.GRAPHENE_JWT_ALGORITHM,
    ).decode('utf-8')


def jwt_decode(token):
    return jwt.decode(
        token,
        jwt_settings.GRAPHENE_JWT_SECRET_KEY,
        True,
        options={
            'verify_exp': True,
        },
        algorithms=[jwt_settings.GRAPHENE_JWT_ALGORITHM],
    )


def get_authorization_header(request):
    auth = request.META.get(jwt_settings.GRAPHENE_JWT_AUTH_HEADER_NAME, '').split()
    prefix = jwt_settings.GRAPHENE_JWT_AUTH_HEADER_PREFIX

    if len(auth) != 2 or auth[0].lower() != prefix.lower():
        return None
    return auth[1]


def get_credentials(request, **kwargs):
    return get_authorization_header(request)


def get_payload(token):
    try:
        payload = jwt_decode(token)
    except jwt.ExpiredSignature:
        raise JSONWebTokenExpired()
    except jwt.DecodeError:
        raise JSONWebTokenError(_('Error decoding signature'))
    except jwt.InvalidTokenError:
        raise JSONWebTokenError(_('Invalid token'))
    return payload


def get_user_by_payload(payload):
    user_id = payload.get('id', None)
    if not user_id:
        raise JSONWebTokenError(_('Invalid JWT Payload'))
    user = UserModel.objects.filter(id=user_id).first()

    if user is not None and not user.is_active:
        raise JSONWebTokenError(_('User is disabled'))
    return user


def refresh_has_expired(orig_iat):
    return timegm(datetime.utcnow().utctimetuple()) > (
            orig_iat + jwt_settings.GRAPHENE_JWT_REFRESH_EXPIRATION_DELTA.total_seconds()
    )


def create_refresh_token(user):
    from django_graphene_jwt.models import RefreshToken
    return RefreshToken.objects.create(user=user)
