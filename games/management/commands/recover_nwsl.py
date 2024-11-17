from django.core.management.base import BaseCommand, CommandError


import datetime
import time
import json
import csv
import pytz

from django.utils import timezone

from games.models import Game, League, Team, Network, WatchLink, Sport
from .utils import str2bool

class Command(BaseCommand):
    """
    Delete games from a certain league or all games from past
    """
    help = 'Recover NWSL games'

    # def nwsl():
    #     counter = 0
    #     response = requests.get(NWSL_ENDPOINT)
    #     json = response.json()
    #     data = json.get('data')
    #     matches = data.get('matches')
    #     # create sport
    #     sport, created = Sport.objects.get_or_create(name='soccer')
    #     # create league
    #     league, created = League.objects.get_or_create(name='NWSL', sport=sport)
    #     for match in matches:
    #         for event in match['events']:
    #             home_team = event.get('team')
    #             opponent = event.get('opponent')
    #             stream = event.get('stream')
    #             if home_team and opponent:
    #                 home_team_name = home_team.get('title')
    #                 opponent_name = opponent.get('title')
    #                 # create team
    #                 home_team, created = Team.objects.get_or_create(name=home_team_name, league=league)
    #                 opponent, created = Team.objects.get_or_create(name=opponent_name, league=league)
    #                 # create network
    #                 network_name = None
    #                 watch_link = None
    #                 if stream:
    #                     network_name = stream.get('title')
    #                     network, created = Network.objects.get_or_create(name=network_name)
    #                     # create watch link
    #                     url = stream.get('url')
    #                     if url:
    #                         watch_link, created = WatchLink.objects.get_or_create(label=network_name, url=url)


    #                 # create game
    #                 date = event.get('date')
    #                 if date:
    #                     date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
    #                     eastern_timezone = pytz.timezone('US/Eastern')
    #                     game_date = eastern_timezone.localize(date)
    #                     game_date = date.astimezone(timezone.utc)
    #                     game, created_game = Game.objects.get_or_create(name=f"{home_team_name} vs {opponent_name}", league=league, sport=sport, time=game_date)

    #                     if created_game:
    #                         game.teams.add(home_team)
    #                         game.teams.add(opponent)
    #                         game.networks.add(network)
    #                         if watch_link:
    #                             game.watch_links.add(watch_link)
    #                         game.save()
    #                         counter += 1
    #     return counter         

    
    def handle(self, *args, **options):


        # get nwsl json
        json_file = 'games/data/nwsl.json'

        sport, created = Sport.objects.get_or_create(name='soccer')
        # create league
        league, created = League.objects.get_or_create(name='NWSL', sport=sport)

        # read json
        import json
        with open(json_file) as f:
            data = json.load(f)
            results = data['results']
            counter = 0
            for result in results:
                # get game
                teams = result['teams']
                home_team = teams[0]
                away_team = teams[1]
                #create teams
                home_team, created = Team.objects.get_or_create(name=home_team.get('name'), league=league)
                away_team, created = Team.objects.get_or_create(name=away_team.get('name'), league=league)

                # time
                date = result.get('time')
                # strip timezone
                date = date[:-6]
                # 2024-03-16T13:00:00-05:00
                date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                current_timezone = pytz.timezone('US/Eastern')
                game_date = current_timezone.localize(date)
                # time is in eastern timezone
                # convert to utc
                game_date = game_date.astimezone(timezone.utc)
                
                
                name = result.get('name')

                # create network
                networks = result.get('network')

                if networks:
                    for network in networks:
                        network_name = network.get('name')
                        network, created = Network.objects.get_or_create(name=network_name)

                # create watch link
                watch_links = result.get('watch_links')
                if watch_links:
                    for watch_link in watch_links:
                        url = watch_link.get('url')
                        label = watch_link.get('label')
                        watch_link, created = WatchLink.objects.get_or_create(label=label, url=url)
                # create game
                game, game_created = Game.objects.get_or_create(name=name, league=league, sport=sport, time=game_date)
                
                if game_created:
                    game.teams.add(home_team)
                    game.teams.add(away_team)
                    if networks:
                        game.networks.add(network)
                    if watch_links:
                        game.watch_links.add(watch_link)
                    game.save()
                    counter += 1
                    print(f"Game {game.name} created")
        print(f"{counter} games created")
        

