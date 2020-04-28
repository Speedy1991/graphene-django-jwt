from django.core.management.base import BaseCommand
from django.template.defaultfilters import pluralize

from graphene_django_jwt.blacklist import Blacklist
from graphene_django_jwt.models import RefreshToken


class Command(BaseCommand):
    help = 'Build initial blacklist'

    def handle(self, *args, **options):
        qs = RefreshToken.objects.filter(revoked__isnull=False)
        for refresh_token in qs.all():
            Blacklist.set(refresh_token)

        no = qs.count()
        msg = 'Successfully blacklisted {} token{}'.format(
            no,
            pluralize(no))

        self.stdout.write(self.style.SUCCESS(msg))
