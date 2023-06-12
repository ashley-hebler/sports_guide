from datetime import date, datetime, timedelta
from django.http import HttpResponse
from django.template import loader

from .models import Game, League, Team

def index(request):
    # games today
    games_today = Game.objects.filter(time__date=date.today()).order_by('time')
    games_this_week = Game.objects.filter(time__date__range=[date.today(), date.today() + timedelta(days=7)]).order_by('time')
    template = loader.get_template('games/index.html')
    # surface networks
    context = {
        'games_today': games_today,
        'games_this_week': games_this_week,
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


from datetime import datetime

from django.http import HttpResponse
