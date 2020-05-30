import json
from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from graphene_django_jwt.utils import create_refresh_token, jwt_encode, jwt_payload


UserModel = get_user_model()


def query_helper(client, query, op_name=None, variables=None):
    body = {'query': query}
    if op_name:
        body['operation_name'] = op_name
    if variables:
        body['variables'] = variables

    resp = client.post('/', json.dumps(body), content_type='application/json')
    return json.loads(resp.content.decode())


class ApiTokenTestCase(TestCase):

    def get_user(self):
        return UserModel.objects.create_user(username='test@graphene_django_jwt.com', password='123')

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
            self._client = Client(HTTP_AUTHORIZATION='Bearer %s' % self.token)
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
            variables,
        )

    def mutate(self, mutation, op_name=None, variables=None):
        return
