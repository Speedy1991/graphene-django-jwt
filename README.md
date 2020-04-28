[![Build Status](https://travis-ci.org/Speedy1991/graphene-django-jwt.svg?branch=master)](https://travis-ci.org/Speedy1991/graphene-django-jwt)


Inspiration
----------
Why another jwt package for Graphene/Graphql?
There are great tools like [django-graphql-jwt](https://github.com/flavors/django-graphql-jwt) and to be honest, this project is heavily based on it.
Some parts are refactored to get rid of some functionallity which isn't related to a jwt framework (IMO):

E.g.:
- Field based token access
- Missing blacklist
- To much configuration options


You can't just revoke a JWT-Refreshtoken, because while it is revoked the user is still able to login until the JWT expires. You need to blacklist the refreshToken to block every related JWT.

Therefore I started this package, because my [Issue](https://github.com/flavors/django-graphql-jwt/issues/60) and [PR](https://github.com/flavors/django-graphql-jwt/pull/62) was not accepted.
In my opinion a blacklist for RefreshTokens is a _must have_ to prevent unauthorized user from stealing JWT's (even it is not [RFC](https://tools.ietf.org/html/rfc7519) conform).

To reduce Database roundtrips this framework is heavily cache based.


Example
-------
You can find an example app in the example folder. For a quick look you can use the docker-compose script like this:

`docker-compose up --force-recreate --build`

Available Endpoints:

```
Admin: http://127.0.0.1:8000/admin
Graphiql: http://127.0.0.1:8000/graphiql
Api: http://127.0.0.1:8000/
```

Credentials: admin:admin

You can find more examples in the example directory


Install
-------
(COMMING SOON)
`pip install graphene-django-jwt`

Add `graphene_django_jwt` to your `INSTALLED_APPS` like this:
```
    ...
    'graphene_django',
    'graphene_django_jwt',
```

You can append the jwt endpoints to your existing `schema.py` like this:
```
from django_graphene_jwt.schema.mutations import Mutation as JWTMutations
from django_graphene_jwt.decorators import login_required

class Mutation(JWTMutations):
    pass


class Query(graphene.ObjectType):
    ... query stuff
    hello_protected = graphene.String(required=True)

    ... resolvers
    @login_required
    def resolve_hello_protected(self, info):
        return 'Hello from protected field'


schema = graphene.Schema(query=Query, mutation=Mutation)
```

You can use the `login_required` decorator on any `resolver` or `mutate` function

Decorators
----------
There are several predefined decorators like:
```
login_required
staff_member_required
superuser_required
permission_required -> takes a single permission or an permission array
user_passes_test(test_func) -> takes a function with a user argument returning True/False
```


Management
----------
You should cleanup your expired tokens periodically, maybe once a day and each serverstart with:

`python manage.py cleartokens --expired`

You should also build your blacklist on server start with:

`python manage.py buildblacklist`
