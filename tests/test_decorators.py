from tests import ApiTokenTestCase


class DecoratorTests(ApiTokenTestCase):

    def set_http_auth_header(self):
        return False

    def test_revoke_all(self):
        resp = self.query("""
            mutation RevokeAll {
              jwtRevokeAllTokens {
                revokedTokens
              }
            }
        """)
        self.assertIsNotNone(resp['errors'])
        self.assertEqual(resp['errors'][0]['code'], 401)
