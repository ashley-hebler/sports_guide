import requests
import re
import datetime
import time

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from games.models import Game, Team, League, Sport, Network



WNBA_ENDPOINT = 'https://data.wnba.com/data/5s/v2015/json/mobile_teams/wnba/2023/league/10_full_schedule_tbds.json'

NCAA_ENDPOINT = 'https://www.espn.com/womens-college-basketball/schedule/_/date/'

PHL_ENDPOINT = 'https://www.oursportscentral.com/services/schedule/premier-hockey-federation/l-231'

NWSL_ENDPOINT = 'https://d2nkt8hgeld8zj.cloudfront.net/services/nwsl.ashx/schedule?season'

CREATE_DATA = True


class Command(BaseCommand):
    help = 'Adds games to the database'

    def nwsl():
        counter = 0
        response = requests.get(NWSL_ENDPOINT)
        json = response.json()
        data = json.get('data')
        matches = data.get('matches')
        # create sport
        sport, created = Sport.objects.get_or_create(name='soccer')
        # create league
        league, created = League.objects.get_or_create(name='NWSL', sport=sport)
        for match in matches:
            for event in match['events']:
                home_team = event.get('team')
                opponent = event.get('opponent')
                stream = event.get('stream')
                if home_team and opponent:
                    home_team_name = home_team.get('title')
                    opponent_name = opponent.get('title')
                    # create team
                    home_team, created = Team.objects.get_or_create(name=home_team_name, league=league)
                    opponent, created = Team.objects.get_or_create(name=opponent_name, league=league)
                    # create network
                    network_name = None
                    if stream:
                        network_name = stream.get('title')
                        network, created = Network.objects.get_or_create(name=network_name)
                    # create game
                    date = event.get('date')
                    if date:
                        date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
                        game_date = date.astimezone(timezone.utc)
                        game, created_game = Game.objects.get_or_create(name=f"{home_team_name} vs {opponent_name}", league=league, sport=sport, network=network, time=game_date)

                        if created_game:
                            game.teams.add(home_team)
                            game.teams.add(opponent)
                            game.save()
                            counter += 1
        return counter         


    def wnba():
        counter = 0
        response = requests.get(WNBA_ENDPOINT)
        data = response.json()
        months = data['lscd']
        for month in months:
            games = month['mscd']['g']
            for game in games:
                home = game['h']
                home_city = home['tc']
                home_name = home['tn']
                visitor = game['v']
                visitor_city = visitor['tc']
                visitor_name = visitor['tn']
                team_home = f'{home_city} {home_name}'
                team_visitor = f'{visitor_city} {visitor_name}'
                
                game_day = game['gdtutc']
                game_time = game['utctm']
                if game_time == 'TBD' or game_time == 'TBD':
                    # skip game
                    continue
                # format is 2023-05-1300:00
                game_date = datetime.datetime.strptime(game_day + game_time + ' +0000', '%Y-%m-%d%H:%M %z')
                # convert to utc
                game_date = game_date.astimezone(timezone.utc)

                # create a sport if it doesn't exist
                sport, created = Sport.objects.get_or_create(name='basketball')
                # create a league if it doesn't exist
                league, created = League.objects.get_or_create(name='WNBA', sport=sport)
                # create a team if it doesn't exist
                team_home, created_home = Team.objects.get_or_create(name=team_home, league=league)
                team_visitor, created_visitor = Team.objects.get_or_create(name=team_visitor, league=league)

                # create a game
                game, created_game = Game.objects.get_or_create(name=f"{team_home} vs {team_visitor}", time=game_date, league=league, sport=sport)
                counter += 1
                if created_game:
                    game.teams.add(team_home)
                    game.teams.add(team_visitor)
                    game.save()
        return counter
        
    def ncaa():
        counter = 0
        # date format is YYYYMMDD
        # todays date
        today_date = datetime.date.today()
        #convert to string
        today = today_date.strftime('%Y%m%d')
        #get dates for the next 7 days
        dates = []
        for i in range(7):
            date = today_date + datetime.timedelta(days=i)
            dates.append({
                'date_str': date.strftime('%Y%m%d'),
                'date': date
            })
        # create sport
        sport, created = Sport.objects.get_or_create(name='basketball')
        # create league
        league, created = League.objects.get_or_create(name='NCAA', sport=sport)
        
        for date in dates:
            date_str = date['date_str']
            page = requests.get(NCAA_ENDPOINT + date_str)
            soup = BeautifulSoup(page.content, "html.parser")
            rows = soup.find_all("tr", class_="Table__TR")
            for row in rows:
                # find team
                teams = row.find_all("span", class_="Table__Team")
                team_names = [team.text for team in teams]
                game_name = ' vs '.join(team_names)
                network_selector = row.select_one(".Logo__Network img")
                if network_selector:
                    network_name = network_selector.attrs['alt']
                else:
                    network_name = None
                date_selector = row.select_one(".date__col")
                if date_selector:
                    time_string = date_selector.text
                    start_time_str = date_str + time_string + ' -0500'
                    if time_string == 'LIVE':
                        # set start time to current time
                        start_time = datetime.datetime.now(tz=timezone.utc)
                    else:
                        start_time = datetime.datetime.strptime(start_time_str, '%Y%m%d%I:%M %p %z')
                        start_time = start_time.astimezone(timezone.utc)
                else:
                    continue
                # create game
                if CREATE_DATA:
                    game, created_game = Game.objects.get_or_create(name=game_name, time=start_time, league=league, sport=sport)
                    counter += 1
                    if created_game:
                        if network_name:
                            # create network
                            network, network_created = Network.objects.get_or_create(name=network_name)
                            # add network to game
                            game.network = network
                            game.save()
                        for team in team_names:
                            # remove rank from team name
                            team = re.sub(r'\d+', '', team).strip()
                            team, created_team = Team.objects.get_or_create(name=team, league=league)
                            game.teams.add(team)
                            game.save()
            # pause 5 seconds
            time.sleep(3)
        return counter
            
    def phl():
        counter = 0
        page = requests.get(PHL_ENDPOINT)
        soup = BeautifulSoup(page.content, "html.parser")
        rows = soup.find_all("tr", class_="sked")
        for row in rows:
            time_selector = row.select_one("td:last-child")
            if time_selector and time_selector.text != 'Final' and time_selector.text != 'Ppd.':
                time_str = time_selector.text
                # convert p.m. to pm and make uppercase
                time_str = time_str.replace('p.m.', 'PM').replace('a.m.', 'AM').upper()                
                date_selector = row.select_one("td:first-child")
                # eastern time offset
                date_str = date_selector.text + ' ' + time_str + ' -0500'
                # add 0 in front of single digit days
                date = datetime.datetime.strptime(date_str, '%B %d, %Y %I:%M %p %z')
                date = date.astimezone(timezone.utc)
                # get links
                links = row.select("a")
                # create sport
                sport, created = Sport.objects.get_or_create(name='hockey')
                # create league
                league, created = League.objects.get_or_create(name='PHL', sport=sport)
                teams = []
                for link in links:
                    team_name = link.text
                    teams.append(team_name)
                # create name from links
                game_name = ' vs '.join(teams)
                if CREATE_DATA:
                    network, network_created = Network.objects.get_or_create(name='ESPN+')
                    game, created_game = Game.objects.get_or_create(name=game_name, time=date, league=league, sport=sport, network=network)
                    counter += 1
                    if created_game:
                        for team in teams:
                            team, created_team = Team.objects.get_or_create(name=team, league=league)
                            game.teams.add(team)
                            game.save()
        return counter        

    def add_arguments(self, parser):
        parser.add_argument('fresh_data', type=bool, help='Delete all games, teams, leagues, networks, and sports before adding new data', default=False)

    def handle(self, *args, **options):
        # get args
        FRESH_DATA = options['fresh_data']
        # if fresh data is needed, delete all games, teams, leagues, networks, and sports
        if FRESH_DATA:
            Game.objects.all().delete()
            Team.objects.all().delete()
            League.objects.all().delete()
            Sport.objects.all().delete()
            Network.objects.all().delete()
        try:
            nwsl = Command.nwsl()
            self.stdout.write(self.style.SUCCESS(f'Successfully added {nwsl} NWSL games'))
        except Exception as e:
            raise CommandError(f'Error adding games: {e}')
    
        try:
            wnba_count = Command.wnba()
            self.stdout.write(self.style.SUCCESS(f'Successfully added {wnba_count} WNBA games'))
        except Exception as e:
            raise CommandError(f'Error adding games: {e}')

        # try:
        #     phl_count = Command.phl()
        #     self.stdout.write(self.style.SUCCESS(f'Successfully added {phl_count} PHL games'))
        # except Exception as e:
        #     raise CommandError(f'Error adding games: {e}')

        # try:
        #     ncaa_count = Command.ncaa()
        #     self.stdout.write(self.style.SUCCESS(f'Successfully added {ncaa_count} NCAA games'))
        # except Exception as e:
        #     raise CommandError(f'Error adding games: {e}')

