from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, viewsets
from datetime import date, timedelta
from games.models import Game, Sport
from .serializers import GameSerializer, SportsSerializer

class GameList(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sport', 'time', 'league']

    def get_queryset(self):
        """
        Optionally filter by date range
        """
        queryset = queryset = Game.objects.all()
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        if start_time and end_time:
            queryset = queryset.filter(time__range=[start_time, end_time])
        return queryset

class GamesToday(generics.ListCreateAPIView):
    queryset = Game.objects.filter(time__date=date.today()).order_by('time')
    serializer_class = GameSerializer

class GamesUpcoming(generics.ListCreateAPIView):
    # games this week after today
    # limit to 20 games
    queryset = Game.objects.filter(time__date__range=[date.today()+ timedelta(days=1), date.today() + timedelta(days=7)]).order_by('time')
    serializer_class = GameSerializer

class SportsList(generics.ListCreateAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportsSerializer