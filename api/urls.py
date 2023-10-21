from django.urls import path
from .views import GameList, GamesToday, GamesUpcoming, SportsList, TeamsList

urlpatterns = [
    path('games/', GameList.as_view()),
    path('sports/', SportsList.as_view()),
    path('today/', GamesToday.as_view()),
    path('upcoming/', GamesUpcoming.as_view()),
    path('teams/', TeamsList.as_view()),
]