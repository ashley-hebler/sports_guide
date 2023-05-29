# from django.urls import path

# from . import views


# urlpatterns = [
#     path('', views.index, name='index'),
# ]

# example/urls.py
from django.urls import path

from games.views import index


urlpatterns = [
    path('', index),
]