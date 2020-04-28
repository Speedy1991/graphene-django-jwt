import json
import logging
import traceback

from django.conf import settings
# import sentry_sdk
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from graphene_django.views import GraphQLView
from graphql.error import GraphQLError, GraphQLSyntaxError
from graphql.error import format_error as format_graphql_error
from graphql.error.located_error import GraphQLLocatedError

from graphene_django_jwt.exceptions import GrapheneDjangoJWTBaseException

logger = logging.getLogger('api.patches')


class BaseException(Exception):
    default_message = _('An server error occurred. A Bug report was created')
    code = 500


def format_internal_error(error, code=None):
    ret = {
        'message': str(error) or str(getattr(error, 'default_message', '')),
        'payload': getattr(error, 'payload', None),
        'code': code or getattr(error, 'code', 500),
    }
    if settings.DEBUG:
        ret['exception'] = type(error).__name__
        ret['trace'] = traceback.format_list(traceback.extract_tb(error.__traceback__))
    logger.info(json.dumps(ret, indent=2))
    return ret


class PatchedGraphQLView(GraphQLView):

    @staticmethod
    def format_error(original_error):
        error = getattr(original_error, 'original_error', original_error)
#        sentry_sdk.capture_exception(original_error)
        if isinstance(original_error, GraphQLLocatedError) or isinstance(original_error, GraphQLError):
            if isinstance(error, ValidationError):
                return format_internal_error(error, code=400)
            if isinstance(error, GrapheneDjangoJWTBaseException):
                return format_internal_error(error)
            if settings.DEBUG:
                return format_internal_error(error)
            else:
                return format_internal_error(BaseException())
        if isinstance(error, GraphQLSyntaxError):
            return format_graphql_error(error)
        else:
            if settings.DEBUG:
                return format_internal_error(error)
            else:
                return format_internal_error(BaseException())

    def execute_graphql_request(self, request, data, query, variables, operation_name, show_graphiql=False):
        logger.info(f'OPERATION: {operation_name}')
        return super(PatchedGraphQLView, self).execute_graphql_request(
            request, data, query, variables, operation_name, show_graphiql=show_graphiql,
        )
