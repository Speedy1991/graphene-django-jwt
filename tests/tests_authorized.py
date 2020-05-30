import time

from tests import ApiTokenTestCase

from graphene_django_jwt.blacklist import Blacklist
from graphene_django_jwt.utils import create_refresh_token


class AuthorizedTests(ApiTokenTestCase):

    def test_revoke_all_gql(self):
        additional_refresh_token = create_refresh_token(self.user).get_token()
        resp = self.query("""
            mutation RevokeAll {
              jwtRevokeAllTokens {
                revokedTokens
              }
            }
        """)
        expected_result = {
            'jwtRevokeAllTokens': {
                'revokedTokens': [self.refresh_token, additional_refresh_token],
            },
        }
        self.assertResponseNoErrors(resp, expected_result)

    def test_obtain_jwt_mutation_gql(self):
        resp = self.query("""
            mutation SignIn {
              jwtSignIn(username: "test@graphene_django_jwt.com", password: "123") {
                token
                refreshToken
              }
            }
        """)
        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertIsNotNone(resp['data']['jwtSignIn']['token'], 'Received token')
        self.assertIsNotNone(resp['data']['jwtSignIn']['refreshToken'], 'Received refreshToken')

    def test_refresh_token(self):
        time.sleep(3)
        refreshed_token = self.refresh_token_obj.rotate()
        self.assertTrue(refreshed_token.created > self.refresh_token_obj.created)

    def test_refresh_token_gql(self):
        time.sleep(3)
        resp = self.query("""
           mutation RefreshToken {
             jwtRefreshToken(refreshToken: "%s") {
               token
               payload
               refreshToken
             }
           }
        """ % self.refresh_token)
        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertIsNotNone(resp['data']['jwtRefreshToken']['token'])
        self.assertIsNotNone(resp['data']['jwtRefreshToken']['refreshToken'])
        self.assertTrue(resp['data']['jwtRefreshToken']['refreshToken'] != self.refresh_token)

    def test_revoke_token(self):
        self.refresh_token_obj.revoke()
        self.assertTrue(Blacklist.is_blacklisted(self.refresh_token))
        self.assertTrue(self.refresh_token_obj.revoked)

    def test_revoke_token_gql(self):
        resp = self.query("""
            mutation RevokeToken {
              jwtRevokeToken(refreshToken:"%s") {
                revoked
              }
            }
        """ % self.refresh_token)

        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertIsNotNone(resp['data']['jwtRevokeToken']['revoked'], 'Revoked Token')
        self.assertTrue(Blacklist.is_blacklisted(self.refresh_token))

    def test_logout_gql(self):
        resp = self.query("""
            mutation Logout {
              jwtLogout(refreshToken: "%s") {
                success
              }
            }
        """ % self.refresh_token)

        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertTrue(resp['data']['jwtLogout']['success'], 'Logout failed')
        self.assertTrue(Blacklist.is_blacklisted(self.refresh_token))
