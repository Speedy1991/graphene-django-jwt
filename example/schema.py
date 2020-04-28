import graphene

from graphene_django_jwt.decorators import login_required
from graphene_django_jwt.schema.mutations import Mutation as JWTMutations


class Mutation(JWTMutations):
    pass


class Query(graphene.ObjectType):
    hello = graphene.String(required=True)
    hello_protected = graphene.String(required=True)

    def resolve_hello(self, info):
        return 'Hello'

    @login_required
    def resolve_hello_protected(self, info):
        return 'Hello from protected field'


schema = graphene.Schema(query=Query, mutation=Mutation)
