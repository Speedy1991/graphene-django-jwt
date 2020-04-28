from django.utils.translation import ugettext_lazy as _


class GrapheneDjangoJWTBaseException(Exception):
    default_message = _('You do not have permission to perform this action')
    code = 401


class JSONWebTokenError(GrapheneDjangoJWTBaseException):
    pass


class PermissionDenied(GrapheneDjangoJWTBaseException):
    default_message = _('You do not have permission to perform this action')
    code = 401


class JSONWebTokenExpired(GrapheneDjangoJWTBaseException):
    default_message = _('Signature has expired')
    code = 401


class JSONRefreshTokenExpired(GrapheneDjangoJWTBaseException):
    default_message = _('Refresh token has expired')
    code = 401
