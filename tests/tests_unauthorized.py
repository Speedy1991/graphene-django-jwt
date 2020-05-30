from tests import ApiTokenTestCase
from django.test import Client


class UnAuthorizedTests(ApiTokenTestCase):

    def set_http_auth_header(self):
        return False

    def test_sign_up(self):
        pass

    def test_verify_token(self):
        pass


class TestInvalidToken(ApiTokenTestCase):

    def setUp(self):
        super(TestInvalidToken, self).setUp()
        self._client = Client(HTTP_AUTHORIZATION='Bearer %s' % 'abc')

    def test_invalid_token(self):
        resp = self.query("""
            mutation RevokeAll {
              jwtRevokeAllTokens {
                revokedTokens
              }
            }
        """)
        self.assertIsNotNone(resp['errors'])
        self.assertEqual(resp['errors'][0]['code'], 401)
