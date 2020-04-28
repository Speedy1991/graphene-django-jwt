import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from graphene_django_jwt.utils import create_refresh_token, jwt_encode, jwt_payload

UserModel = get_user_model()


def query_helper(client, query, op_name=None, variables=None):
    body = {'query': query}
    if op_name:
        body["operation_name"] = op_name
    if variables:
        body["variables"] = variables

    resp = client.post('/', json.dumps(body), content_type="application/json")
    return json.loads(resp.content.decode())


class ApiTokenTestCase(TestCase):

    def get_user(self):
        return UserModel.objects.create_user(username="test@graphene_django_jwt.com", password="123")

    def set_http_auth_header(self):
        return True

    def setUp(self):
        user = self.get_user()
        refresh_token = create_refresh_token(user).get_token()
        payload = jwt_payload(user, refresh_token=refresh_token)
        token = jwt_encode(payload)

        self.refresh_token = refresh_token
        self.token = token
        self.user = user

        if self.set_http_auth_header():
            self._client = Client(HTTP_AUTHORIZATION="Bearer %s" % self.token)
        else:
            self._client = Client()

    def assertResponseNoErrors(self, resp, expected):
        self.assertNotIn('errors', resp, 'Response had errors')
        self.assertEqual(resp['data'], expected, 'Response has correct data')

    def query(self, query, op_name=None, variables=None):
        return query_helper(
            self._client,
            query,
            op_name,
            variables
        )

    def mutate(self, mutation, op_name=None, variables=None):
        return


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
            "jwtRevokeAllTokens": {
              "revokedTokens": [self.refresh_token, additional_refresh_token]
            }
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
        self.assertIsNotNone(resp['data']["jwtSignIn"]["token"], 'Received token')
        self.assertIsNotNone(resp['data']["jwtSignIn"]["refreshToken"], 'Received refreshToken')

    def test_refresh_token(self):
        pass

    def test_refresh_expired_token(self):
        pass

    def test_revoke_token(self):
        pass

    def test_logout(self):
        pass


class UnAuthorizedTests(ApiTokenTestCase):

    def set_http_auth_header(self):
        return False

    def test_sign_up(self):
        pass

    def test_verify_token(self):
        pass


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
        self.assertIsNotNone(resp["errors"])
        self.assertEqual(resp["errors"][0]["code"], 401)


class TestInvalidToken(ApiTokenTestCase):

    def setUp(self):
        super(TestInvalidToken, self).setUp()
        self._client = Client(HTTP_AUTHORIZATION="Bearer %s" % "abc")

    def test_invalid_token(self):
        resp = self.query("""
            mutation RevokeAll {
              jwtRevokeAllTokens {
                revokedTokens
              }
            }
        """)
        self.assertIsNotNone(resp["errors"])
        self.assertEqual(resp["errors"][0]["code"], 401)
