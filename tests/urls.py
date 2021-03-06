from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from graphene_django_jwt.patches import PatchedGraphQLView

urlpatterns = [
    path('', csrf_exempt(PatchedGraphQLView.as_view())),
    path('graphiql/', csrf_exempt(PatchedGraphQLView.as_view(graphiql=True))),
    path('admin/', admin.site.urls),
]
