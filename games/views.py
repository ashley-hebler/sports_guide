from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.template import loader

from .models import Game, League, Team

def index(request):
    # all game sorted by time and starting with today
    today = date.today()
    games = Game.objects.filter(time__gte=today).order_by('time')[:300]
    template = loader.get_template('games/index.html')
    context = {
        'games': games,
    }
    return HttpResponse(template.render(context, request))


# leagues
def leagues(request):
    # leagues = League.objects.order_by('-name')
    leagues = {}
    games = Game.objects.order_by('time')[:1000]
    for game in games:
        league_name = game.league.name
        if leagues.get(league_name) is None:
            leagues[league_name] = {
                'name': league_name,
                'games': [game],
            }
        else:
            leagues[league_name]['games'].append(game)
    # convert to list
    leagues = list(leagues.values())
    template = loader.get_template('games/leagues.html')
    context = {
        'leagues': leagues,
    }
    return HttpResponse(template.render(context, request))


# teams
def teams(request):
    # all teams
    teams = Team.objects.order_by('name')
    template = loader.get_template('games/teams.html')
    context = {
        'teams': teams,
    }
    return HttpResponse(template.render(context, request))
