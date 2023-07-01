from django.urls import path
from .views import GameList, GamesToday, GamesUpcoming

urlpatterns = [
    path('', GameList.as_view()),
    path('today/', GamesToday.as_view()),\
    path('upcoming/', GamesUpcoming.as_view()),
]