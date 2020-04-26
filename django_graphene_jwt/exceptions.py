from django.utils.translation import ugettext_lazy as _


class JSONWebTokenError(Exception):
    pass


class PermissionDenied(Exception):
    default_message = _('You do not have permission to perform this action')
    code = 401


class JSONWebTokenExpired(Exception):
    default_message = _('Signature has expired')
    code = 401


class JSONRefreshTokenExpired(Exception):
    default_message = _('Refresh token has expired')
    code = 401
