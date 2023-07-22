import datetime

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, viewsets

from games.models import Game, Sport
from .serializers import GameSerializer, SportsSerializer

class GameList(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sport', 'time', 'league']

    def get_queryset(self):
        """
        Parmaeters:
        ?start_time=YYYY-MM-DD&end_time=YYYY-MM-DD
        ?start_time=YYYY-MM-DD
        ?current=true
        """
        queryset = Game.objects.all().order_by('time')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        current = self.request.query_params.get('current')
        if start_time and end_time:
            queryset = queryset.filter(time__range=[start_time, end_time])
        if start_time and not end_time:
            queryset = queryset.filter(time__gte=start_time)
        if current:
            # remove games that started more than 3 hours ago
            current_time = datetime.datetime.now()
            queryset = queryset.filter(time__gte=current_time - datetime.timedelta(hours=3))
        return queryset

class GamesToday(generics.ListCreateAPIView):
    queryset = Game.objects.filter(time__date=datetime.date.today()).order_by('time')
    serializer_class = GameSerializer

class GamesUpcoming(generics.ListCreateAPIView):
    # games this week after today
    # limit to 20 games
    queryset = Game.objects.filter(time__date__range=[datetime.date.today()+ datetime.timedelta(days=1), datetime.date.today() + datetime.timedelta(days=7)]).order_by('time')
    serializer_class = GameSerializer

class SportsList(generics.ListCreateAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportsSerializer