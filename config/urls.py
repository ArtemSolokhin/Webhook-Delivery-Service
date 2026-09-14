from django.urls import path

from webhooks.api import api

urlpatterns = [
    path("api/", api.urls),
]
