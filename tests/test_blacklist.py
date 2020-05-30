from tests import ApiTokenTestCase

from graphene_django_jwt.blacklist import Blacklist


class AuthorizedTests(ApiTokenTestCase):

    def test_blacklist(self):
        Blacklist.set(self.refresh_token)
        self.assertTrue(Blacklist.is_blacklisted(self.refresh_token))
