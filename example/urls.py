from django.contrib import admin
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from .patches import PatchedGraphQLView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('graphiql/', csrf_exempt(PatchedGraphQLView.as_view(graphiql=True))),
]
