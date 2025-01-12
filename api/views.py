import datetime

from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import generics, viewsets

from games.models import Game, Sport, Team
from .serializers import GameSerializer, SportsSerializer, TeamSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.exceptions import ValidationError

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
        ?team_includes=team_name
        ?team=team_id
        ?network=network_id
        """
        queryset = Game.objects.all().order_by('time')
        start_time = self.request.query_params.get('start_time')
        end_time = self.request.query_params.get('end_time')
        current = self.request.query_params.get('current')
        team_includes = self.request.query_params.get('team_includes')
        team = self.request.query_params.get('team')
        network = self.request.query_params.get('network')
        if start_time and end_time:
            queryset = queryset.filter(time__range=[start_time, end_time])
        if start_time and not end_time:
            queryset = queryset.filter(time__gte=start_time)
        if current:
            # remove games that started more than 3 hours ago
            current_time = datetime.datetime.now()
            queryset = queryset.filter(time__gte=current_time - datetime.timedelta(hours=3))
        if team_includes:
            queryset = queryset.filter(teams__name__icontains=team_includes)
        if team:
            queryset = queryset.filter(teams__id=team)
        if network:
            queryset = queryset.filter(networks__id=network)
        return queryset

class GamesToday(generics.ListCreateAPIView):
    queryset = Game.objects.filter(time__date=datetime.date.today()).order_by('time')
    # remove games more than 2 hours ago
    current_time = datetime.datetime.now()
    queryset = queryset.filter(time__gte=current_time - datetime.timedelta(hours=2))
    serializer_class = GameSerializer

class GamesUpcoming(generics.ListCreateAPIView):
    # games this week after today
    # limit to 20 games
    queryset = Game.objects.filter(time__date__range=[datetime.date.today()+ datetime.timedelta(days=1), datetime.date.today() + datetime.timedelta(days=7)]).order_by('time')
    serializer_class = GameSerializer

class SportsList(generics.ListCreateAPIView):
    queryset = Sport.objects.all()
    serializer_class = SportsSerializer

class TeamsList(generics.ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    def get_queryset(self):
        queryset = Team.objects.all()
        sport = self.request.query_params.get('sport')
        league = self.request.query_params.get('league')
        order = self.request.query_params.get('order')
        if sport:
            queryset = queryset.filter(league__sport__name=sport)
        if league:
            # lowercase league name
            league = league.lower()
            # ignore case
            queryset = queryset.filter(league__name__iexact=league)
        # sort by name or order
        
        if order is not None:
            fields = ['rank', '-rank', 'name', '-name']
            if order in fields:
                queryset = queryset.order_by(order)
            else:
                raise ValidationError({'errror': 'order field must be in ' + ', '.join(fields)})
        else:
            queryset = queryset.order_by('name')
        return queryset
    
@method_decorator(cache_page(60 * 60), name='dispatch')  # Cache for 1 hour
class GamesBySport(generics.ListAPIView):
    serializer_class = GameSerializer

    def get_queryset(self):
        sport_name = self.kwargs.get('sport')
        
        # Validate sport exists
        sport_obj = Sport.objects.filter(name__iexact=sport_name).first()
        if not sport_obj:
            raise ValidationError({'error': f'Sport "{sport_name}" not found.'})

        # Use prefetch_related to optimize database queries
        # dont show games more than 24 hours old
        return Game.objects.filter(sport=sport_obj, time__gte=datetime.datetime.now() - datetime.timedelta(days=1)).order_by('time').prefetch_related('teams', 'networks', 'watch_links')