from rest_framework import generics
from datetime import date, timedelta
from games.models import Game
from .serializers import GameSerializer

class GameList(generics.ListCreateAPIView):
    queryset = Game.objects.all()
    serializer_class = GameSerializer

class GamesToday(generics.ListCreateAPIView):
    queryset = Game.objects.filter(time__date=date.today()).order_by('time')
    serializer_class = GameSerializer

class GamesUpcoming(generics.ListCreateAPIView):
    # games this week after today
    # limit to 20 games
    queryset = Game.objects.filter(time__date__range=[date.today()+ timedelta(days=1), date.today() + timedelta(days=7)]).order_by('time')
    serializer_class = GameSerializer