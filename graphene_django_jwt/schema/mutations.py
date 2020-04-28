from calendar import timegm

from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db import transaction

import graphene
from graphene.types.generic import GenericScalar
from graphene_django_jwt import signals
from graphene_django_jwt.blacklist import Blacklist
from graphene_django_jwt.decorators import login_required
from graphene_django_jwt.exceptions import JSONRefreshTokenExpired, JSONWebTokenExpired, PermissionDenied
from graphene_django_jwt.models import RefreshToken
from graphene_django_jwt.shortcuts import get_refresh_token, get_token
from graphene_django_jwt.utils import create_refresh_token, get_payload, jwt_encode, jwt_payload

UserModel = get_user_model()


class RevokeAllTokensMutation(graphene.Mutation):
    revoked_tokens = graphene.List(graphene.NonNull(graphene.String), required=True)

    @login_required
    def mutate(self, info, **kwargs):
        revoked_tokens = []
        for rt in RefreshToken.objects.filter(user_id=info.context.user.id, revoked__isnull=True):
            rt.revoke()
            revoked_tokens.append(rt.get_token())
        return RevokeAllTokensMutation(revoked_tokens=revoked_tokens)


class ObtainJSONWebTokenMutation(graphene.Mutation):
    token = graphene.String(required=True)
    refresh_token = graphene.String(required=True)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    def mutate(self, info, username, password):
        user = UserModel.objects.filter(username=username).first()

        if user is None:
            raise PermissionDenied
        if not user.is_active:
            raise PermissionDenied
        if not user.check_password(password):
            raise PermissionDenied

        refresh_token = create_refresh_token(user).get_token()
        payload = jwt_payload(user, refresh_token=refresh_token)
        token = jwt_encode(payload)
        user_logged_in.send(sender=ObtainJSONWebTokenMutation, request=info.context, user=user)
        return ObtainJSONWebTokenMutation(token=token, refresh_token=refresh_token)


class RefreshMutation(graphene.Mutation):
    token = graphene.String(required=True)
    payload = GenericScalar(required=True)
    refresh_token = graphene.String(required=True)

    class Arguments:
        refresh_token = graphene.String(required=True)

    def mutate(self, info, refresh_token):
        refresh_token = get_refresh_token(refresh_token)

        if refresh_token.revoked:
            raise JSONRefreshTokenExpired
        if refresh_token.is_expired():
            raise JSONRefreshTokenExpired

        refreshed_token = refresh_token.rotate()
        payload = jwt_payload(refresh_token.user, refresh_token=refreshed_token.get_token())
        token = jwt_encode(payload)
        signals.refresh_finished.send(
            sender=RefreshToken,
            user=refresh_token.user,
            request=info.context,
        )
        return RefreshMutation(token=token, payload=payload, refresh_token=refreshed_token.get_token())


class RevokeMutation(graphene.Mutation):
    revoked = graphene.Int(required=True)

    class Arguments:
        refresh_token = graphene.String(required=True)

    def mutate(self, info, refresh_token):
        refresh_token = get_refresh_token(refresh_token)
        refresh_token.revoke()
        return RevokeMutation(revoked=timegm(refresh_token.revoked.timetuple()))


class VerifyMutation(graphene.Mutation):
    payload = GenericScalar(required=True)

    class Arguments:
        token = graphene.String(required=True)

    def mutate(self, info, token):
        payload = get_payload(token)
        if Blacklist.is_blacklisted(payload['refresh_token']):
            raise JSONWebTokenExpired
        return VerifyMutation(payload=payload)


class LogoutMutation(graphene.Mutation):

    success = graphene.Boolean(required=True)

    class Arguments:
        refresh_token = graphene.String(required=False)

    @login_required
    def mutate(self, info, refresh_token=None, **kwargs):
        if refresh_token:
            refresh_token = get_refresh_token(refresh_token)
            refresh_token.revoke()
        user_logged_out.send(sender=self.__class__, request=info.context, user=info.context.user)
        return LogoutMutation(success=True)


class SignUpMutation(graphene.Mutation):

    token = graphene.String(required=True)

    class Arguments:
        password = graphene.String(required=True)
        username = graphene.String(required=True)

    @transaction.atomic
    def mutate(self, info, username, password, **kwargs):
        user = UserModel.objects.create_user(
            username=username,
            password=password,
        )

        refresh_token = create_refresh_token(user)
        token = get_token(
            user,
            refresh_token=refresh_token.token,
        )
        user_logged_in.send(sender=user.__class__, request=info.context, user=user)
        return SignUpMutation(token=token)


class Mutation(graphene.ObjectType):
    jwt_sign_in = ObtainJSONWebTokenMutation.Field(required=True)
    jwt_sign_up = SignUpMutation.Field(required=True)
    jwt_refresh_token = RefreshMutation.Field(required=True)
    jwt_revoke_token = RevokeMutation.Field(required=True)
    jwt_verify_token = VerifyMutation.Field(required=True)
    jwt_revoke_all_tokens = RevokeAllTokensMutation.Field(required=True)
    jwt_logout = LogoutMutation.Field(required=True)
