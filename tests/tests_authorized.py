from tests import ApiTokenTestCase
from graphene_django_jwt.utils import create_refresh_token


class AuthorizedTests(ApiTokenTestCase):

    def test_revoke_all(self):
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

    def test_obtain_jwt_mutation(self):
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
        pass

    def test_refresh_expired_token(self):
        pass

    def test_revoke_token(self):
        pass

    def test_logout(self):
        pass
