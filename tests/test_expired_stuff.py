import time

from tests import ApiTokenTestCase


class ExpiredTests(ApiTokenTestCase):
    def test_refresh_expired_token(self):
        time.sleep(15)
        self.assertTrue(self.refresh_token_obj.is_expired())

    def test_refresh_expired_token_gql(self):
        time.sleep(15)
        resp = self.query("""
            mutation RefreshToken {
              jwtRefreshToken(refreshToken: "%s") {
                token
                payload
                refreshToken
              }
            }
        """ % self.refresh_token)
        self.assertIsNotNone(resp['errors'])
        self.assertEqual(resp['errors'][0]['code'], 401)
