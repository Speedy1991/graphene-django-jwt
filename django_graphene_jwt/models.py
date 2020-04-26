import binascii
import os
from calendar import timegm

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from django_graphene_jwt import managers, signals
from django_graphene_jwt.blacklist import Blacklist
from django_graphene_jwt.utils import refresh_has_expired

UserModel = get_user_model()


class RefreshToken(models.Model):
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name=_('user'),
        related_name='refresh_tokens',
    )

    token = models.CharField(_('token'), max_length=255, editable=False)

    created = models.DateTimeField(_('created'), auto_now_add=True)
    revoked = models.DateTimeField(_('revoked'), null=True, blank=True)

    objects = managers.RefreshTokenQuerySet.as_manager()

    class Meta:
        verbose_name = _('refresh token')
        verbose_name_plural = _('refresh tokens')
        unique_together = ('token', 'revoked')

    def __str__(self):
        return self.token

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self._cached_token = RefreshToken.generate_token()
        super(RefreshToken, self).save(*args, **kwargs)

    @classmethod
    def generate_token(cls):
        return binascii.hexlify(
            os.urandom(20),
        ).decode()

    def get_token(self):
        if hasattr(self, '_cached_token'):
            return self._cached_token
        return self.token

    def is_expired(self):
        orig_iat = timegm(self.created.timetuple())
        return refresh_has_expired(orig_iat)

    def revoke(self):
        self.revoked = timezone.now()
        self.save(update_fields=['revoked'])
        Blacklist.set(self)

        signals.refresh_token_revoked.send(
            sender=RefreshToken,
            refresh_token=self,
        )

    def rotate(self):
        refresh_token = RefreshToken.objects.create(user=self.user)
        # TODO: revoke old one?
        signals.refresh_token_rotated.send(
            sender=RefreshToken,
            refresh_token=self,
        )

        return refresh_token
