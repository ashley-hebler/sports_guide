import requests
import re
import datetime
import time
import json
import csv
import pytz

from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from games.models import Game, Team, League, Sport, Network, WatchLink
from .utils import str2bool



WNBA_ENDPOINT = 'https://data.wnba.com/data/5s/v2015/json/mobile_teams/wnba/2023/league/10_full_schedule_tbds.json'
WNBA_ENDPOINT = 'https://data.wnba.com/data/5s/v2015/json/mobile_teams/wnba/2024/league/10_full_schedule.json'
WNBA_ENDPOINT = 'https://cdn.wnba.com/static/json/staticData/scheduleLeagueV2_1.json'
# this looked promising too https://cdn.wnba.com/static/json/staticData/scheduleLeagueV2_1.json

NCAA_ENDPOINT = 'https://www.espn.com/womens-college-basketball/schedule/_/date/'

PWHL_ENDPOINT = 'https://www.thepwhl.com/en/where-to-watch'

NWSL_ENDPOINT = 'https://nwsl-api-prd-sdp.akamaized.net/v1/nwsl/football/seasons/nwsl::Football_Season::fe17bea0b7234cf7957c7249cb828270/matches?locale=en-US&startDate=2024-01-31&endDate=2024-12-31'

# from https://www.fifa.com/fifaplus/en/tournaments/womens/womensworldcup/australia-new-zealand2023/tv-programme?
FIFA_ENDPOINT = 'https://api.fifa.com/api/v3/calendar/matches?language=en&count=500'
US_SOCCER = 'https://www.ussoccer.com/api/matches/upcoming/contestant/e70zl10x0ayu7y10ry0wi465a'
# US_SOCCER = 'https://www.ussoccer.com/api/scoreboard/contestant/e70zl10x0ayu7y10ry0wi465a,9vh2u1p4ppm597tjfahst2m3n,bo858sll0r8nayyt5smdu3pxs,ec3tww97m7qojokgz53yr44em,7a7uyvix8axi28h7d3bwl4tbe,69m5c06m9up1j8vf8ulnb80xu,x1zdh3b7nwu0ql0uc5tgic9e,bvwww6axicyq6121pawu2fq7k,2vnxw9nc0zq05fdawsdy9mc1n,be84r8u96b8jh66dwbv9b4qjk'
# US_SOCCER = 'https://www.ussoccer.com/api/scoreboard/contestant/e70zl10x0ayu7y10ry0wi465a'

FIFA_NETWORK_LOOKUP = 'https://api.fifa.com/api/v3/watch/season/285026?language=en'

FIFA_NAME_PREFIX = 'World Cup 2023 -'

CREATE_DATA = True

FIFA_TBA = 'TBD'

NCAA_FILE = './games/data/ncaa_data/final.csv'
NCAA_VBALL_FILE = './games/data/ncaa_data_volleyball/final.csv'

NCAA_MARCH_MADNESS = 'https://www.ncaa.com/news/basketball-women/article/2024-03-17/2024-march-madness-womens-ncaa-tournament-schedule-dates-times'

WNBA_CONF_MAP = {
    'Eastern Conference': [
        'Atlanta Dream',
        'Chicago Sky',
        'Connecticut Sun',
        'Indiana Fever',
        'New York Liberty',
        'Washington Mystics',
    ],
    'Western Conference': [
        'Dallas Wings',
        'Las Vegas Aces',
        'Los Angeles Sparks',
        'Minnesota Lynx',
        'Phoenix Mercury',
        'Seattle Storm',
    ]
}

class Command(BaseCommand):
    help = 'Adds games to the database'

    def remove_non_printable(text):
        bad_chars = ['\xa0']
        for char in bad_chars:
            text = text.replace(char, '')
        return text
        
        return cleaned_text

    def month_to_num(month):
        return{
            'January' : 1,
            'February' : 2,
            'March' : 3,
            'April' : 4,
            'May' : 5,
            'June' : 6,
            'July' : 7,
            'August' : 8,
            'September' : 9, 
            'October' : 10,
            'November' : 11,
            'December' : 12
        }[month]

    def convert_local_time_to_utc(local_time_str, city):
        # Define the time zone for the given city
        local_tz = pytz.timezone(city)

        # Parse the local time string to a datetime object
        # format is 01/24/2024 07:00 PM
        local_time = datetime.datetime.strptime(local_time_str, '%m/%d/%Y %I:%M %p')

        # Localize the datetime object to the specified time zone
        local_time = local_tz.localize(local_time)

        # Convert the localized time to UTC
        utc_time = local_time.astimezone(pytz.utc)

        return utc_time

    def nwsl():
        counter = 0
        response = requests.get(NWSL_ENDPOINT)
        json_data = response.json()
        matches = json_data.get('matches')
        # create sport
        sport, created = Sport.objects.get_or_create(name='soccer')
        # create league
        league, created = League.objects.get_or_create(name='NWSL', sport=sport)
        for event in matches:
            home_team = event.get('home')
            opponent = event.get('away')
            stream = event.get('editorial')
            watch_links = []
            networks = []   
            if home_team and opponent:
                home_team_name = home_team.get('mediaName')
                opponent_name = opponent.get('mediaName')
                # create team
                home_team, created = Team.objects.get_or_create(name=home_team_name, league=league)
                opponent, created = Team.objects.get_or_create(name=opponent_name, league=league)
                # create network
                network_name = None
                watch_link = None
                if stream:
                    broadcasts = stream.get('broadcasters')
    
                    for key, value in broadcasts.items():
                        # example ABC|https://www.espn.com/watch/catalog/5cfc4100-6528-4970-8370-21007a36fe3e
                        # split by |
                        if value:
                            network_vals = value.split('|')
                            network_name = network_vals[0]
                            url = network_vals[1]
                            network, created = Network.objects.get_or_create(name=network_name)
                            networks.append(network)
                            # create watch link
                            if url:
                                watch_link, created = WatchLink.objects.get_or_create(label=network_name, url=url)
                                watch_links.append(watch_link)          

                # create game
                date = event.get('matchDateUtc')
                if date:
                    # 2024-03-16T17:00:00Z
                    utc_time = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                    game, created_game = Game.objects.get_or_create(name=f"{home_team_name} vs {opponent_name}", league=league, sport=sport, time=utc_time)

                    if created_game:
                        game.teams.add(home_team)
                        game.teams.add(opponent)
                        for network in networks:
                            game.networks.add(network)
                        for watch_link in watch_links:
                            game.watch_links.add(watch_link)
                        game.save()
                        counter += 1
        
                
        return counter         

    # def wnba():
    #     counter = 0
    #     response = requests.get(WNBA_ENDPOINT)
    #     data = response.json()
    #     months = data['lscd']
    #     for month in months:
    #         games = month['mscd']['g']
    #         for game in games:
    #             home = game['h']
    #             home_city = home['tc']
    #             home_name = home['tn']
    #             visitor = game['v']
    #             visitor_city = visitor['tc']
    #             visitor_name = visitor['tn']
    #             team_home = f'{home_city} {home_name}'
    #             team_visitor = f'{visitor_city} {visitor_name}'
                
    #             game_day = game['gdtutc']
    #             game_time = game['utctm']
    #             if game_time == 'TBD' or game_time == 'TBD':
    #                 # skip game
    #                 continue
    #             # format is 2023-05-1300:00
    #             game_date = datetime.datetime.strptime(game_day + game_time + ' +0000', '%Y-%m-%d%H:%M %z')
    #             # convert to utc
    #             game_date = game_date.astimezone(timezone.utc)

    #             # create a sport if it doesn't exist
    #             sport, created = Sport.objects.get_or_create(name='basketball')
    #             # create a league if it doesn't exist
    #             league, created = League.objects.get_or_create(name='WNBA', sport=sport)
    #             # create a team if it doesn't exist
    #             team_home, created_home = Team.objects.get_or_create(name=team_home, league=league)
    #             team_visitor, created_visitor = Team.objects.get_or_create(name=team_visitor, league=league)

    #             # create network
    #             broadcast = game['bd']
    #             networks = []
    #             if broadcast:
    #                 network_list = broadcast['b']
    #                 if network_list:
    #                     for network in network_list:
    #                         network_name = network['disp']
    #                         network, created = Network.objects.get_or_create(name=network_name)
    #                         networks.append(network)
    #             # create a game
    #             game, created_game = Game.objects.get_or_create(name=f"{team_home} vs {team_visitor}", time=game_date, league=league, sport=sport)
    #             counter += 1
    #             if created_game:
    #                 for network in networks:
    #                     game.networks.add(network)
    #                 game.teams.add(team_home)
    #                 game.teams.add(team_visitor)
    #                 game.save()
    #     return counter
        
    def get_wnba_conf(team_name):
        for conf, teams in WNBA_CONF_MAP.items():
            if team_name in teams:
                return conf
        return None

    def wnba():
        url = WNBA_ENDPOINT
        response = requests.get(url)
        json = response.json()
        schedule = json.get('leagueSchedule')
        game_dates = schedule.get('gameDates')
        # create sport
        sport, created = Sport.objects.get_or_create(name='basketball')
        # create league
        league, created = League.objects.get_or_create(name='WNBA', sport=sport)
        counter = 0
        for game_date in game_dates:
            games = game_date.get('games')
            for game in games:
                date = game.get('gameDateTimeUTC')
                # date is 2024-05-03T04:00:00Z
                game_date = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)
                home_team = game.get('homeTeam')
                home_city = home_team.get('teamCity')
                home_name = home_team.get('teamName')
                home_team_name = f'{home_city} {home_name}'
                home_conf = Command.get_wnba_conf(home_team_name)
                away_team = game.get('awayTeam')
                away_city = away_team.get('teamCity')
                away_name = away_team.get('teamName')
                away_team_name = f'{away_city} {away_name}'
                away_conf = Command.get_wnba_conf(away_team_name)

                # create teams
                home_team, created_home = Team.objects.get_or_create(name=home_team_name, league=league, conference=home_conf)

                away_team, created_away = Team.objects.get_or_create(name=away_team_name, league=league, conference=away_conf)

                # get networks
                broadcasters = game.get('broadcasters')
                # loop through broadcaster keys
                networks = []
                watch_links = []
                for broadcaster in broadcasters.keys():
                    possible_networks = broadcasters.get(broadcaster)
                    if len(possible_networks) > 0:
                        for p_network in possible_networks:
                            network_name = p_network.get('broadcasterAbbreviation')
                            
                            # create network
                            network, created = Network.objects.get_or_create(name=network_name)
                            networks.append(network)

                            #create watch link
                            url = p_network.get('broadcasterVideoLink')
                            if url:
                                watch_link, created = WatchLink.objects.get_or_create(label=network_name, url=url)
                                watch_links.append(watch_link)
                
                # create game
                game_event = game.get('gameLabel')
                game, created_game = Game.objects.get_or_create(name=game_event, league=league, sport=sport, time=game_date)


                if created_game:
                    counter += 1
                    game.teams.add(home_team)
                    game.teams.add(away_team)
                    if len(networks) > 0:
                        for network in networks:
                            game.networks.add(network)
                    if len(watch_links) > 0:
                        for watch_link in watch_links:
                            game.watch_links.add(watch_link)
                    game.save()

        return counter
                    
    # def ncaa():
    #     counter = 0
    #     url = NCAA_MARCH_MADNESS
    #     response = requests.get(url)
    #     soup = BeautifulSoup(response.content, 'html.parser')
    #     headings_that_look_like_dates = soup.find_all('h3')
    #     key_words = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    #     if headings_that_look_like_dates:
    #         for heading in headings_that_look_like_dates:
    #             if any(word in heading.text for word in key_words):
    #                 heading_text = heading.text
    #                 # example Sunday, March 24 — Second round
    #                 heading_split = heading_text.split('—')[0]
    #                 day_full = heading_split.split(',')[1]
    #                 day_split = day_full.strip().split(' ')
    #                 month = Command.month_to_num(day_split[0])
    #                 day = day_split[1]
    #                 day_title = heading_text.split('—')[1]
                    
    #                 games = heading.find_next('ul')
    #                 if games:
    #                     games = games.find_all('li')
    #                     for game in games:
    #                         # example (16) Sacred Heart vs. (16) Presbyterian | 7 p.m. | ESPNU
    #                         # split by |
    #                         game_info = game.text.split('|')
    #                         if len(game_info) == 3:
    #                             teams = game_info[0]
    #                             time = game_info[1]
    #                             network = game_info[2]

    #                             # convert time to datetime (time is Eastern)
    #                             time = time.strip()
    #                             time = time.replace('p.m.', 'PM')
    #                             time = time.replace('a.m.', 'AM')
    #                             # add 00 to time if it's missing
    #                             time_split = time.split(' ')
    #                             time_number = time_split[0]
                                
    #                             if time_number == 'Noon':
    #                                 time_number = '12:00'
    #                                 time_am_pm = 'PM'
    #                             elif len(str(time_number)) < 4:
    #                                 time_number = f'{time_number}:00'
    #                                 time_am_pm = time_split[1]
    #                             else:
    #                                 time = time_number
    #                                 clean_time_split = []
    #                                 for time_section in time_split:
    #                                     clean_time_split.append(Command.remove_non_printable(time_section))
    #                                 if len(clean_time_split) == 2:
    #                                     time_number = clean_time_split[0]
    #                                     time_am_pm = clean_time_split[1]
    #                                 else:
    #                                     #find am or pm
    #                                     time_am_pm = re.findall(r'[AaPp][Mm]', time)[0]
    #                                     # find time
    #                                     time_number = re.findall(r'\d+', time)[0]
    #                                     time_number = f'{time_number}:00'

    #                             # #%m/%d/%Y %I:%M %p
    #                             date_str = f'{month}/{day}/2024 {time_number} {time_am_pm}'
    #                             # convert to utc
    #                             game_date = Command.convert_local_time_to_utc(date_str, 'US/Eastern')

    #                             # split teams by vs.
    #                             teams = teams.split('vs.')
    #                             # get rank from team
    #                             clean_teams = []
    #                             for team in teams:
    #                                 rank = re.findall(r'\d+', team)
    #                                 if len(rank) > 0:
    #                                     rank = rank[0]
    #                                     team = team.replace(rank, '').strip()
    #                                 else:
    #                                     rank = None
    #                                 team = team.strip()
    #                                 # remove empty parentheses
    #                                 team = team.replace('()', '')
    #                                 clean_teams.append((team, rank))
    #                             home_team_name = clean_teams[0][0]
    #                             away_team_name = clean_teams[1][0]
    #                             home_team_rank = clean_teams[0][1]
    #                             away_team_rank = clean_teams[1][1]

    #                             print(f'{home_team_name} vs {away_team_name} on {game_date} on {network}')

    #                             # create sport
    #                             sport, created = Sport.objects.get_or_create(name='basketball')
    #                             # create league
    #                             league, created = League.objects.get_or_create(name='NCAA', sport=sport)
    #                             # create teams
    #                             home_team, created_home = Team.objects.get_or_create(name=home_team_name, league=league, rank=home_team_rank)
    #                             away_team, created_away = Team.objects.get_or_create(name=away_team_name, league=league, rank=away_team_rank)
    #                             # create game
    #                             game, created_game = Game.objects.get_or_create(name=f"{home_team_name} vs {away_team_name}", league=league, sport=sport, time=game_date, event=day_title)

    #                             if created_game:
    #                                 counter += 1
    #                                 game.teams.add(home_team)
    #                                 game.teams.add(away_team)
    #                                 network, created = Network.objects.get_or_create(name=network)
    #                                 game.networks.add(network)
    #                                 game.save()
    #     return counter


    def ncaa():
        CSV_DATA = NCAA_FILE
        counter = 0
        # create a sport if it doesn't exist
        sport, created = Sport.objects.get_or_create(name='basketball')
        # create a league if it doesn't exist
        league, created = League.objects.get_or_create(name='NCAA', sport=sport)

        # open csv file
        with open(CSV_DATA, 'r') as csv_file:
            # skip first line
            next(csv_file)
            # read csv file
            csv_reader = csv.reader(csv_file, delimiter=',')
            # loop through each row
            for row in csv_reader:
                # get date and time
                date = row[0]
                time = row[1]
                # handle when time is Noon
                if time == 'Noon':
                    time = '12:00 PM'
                game_time = date + time
                # convert to datetime (format is 202401117:00 PM)
                try:
                    game_date = datetime.datetime.strptime(game_time, '%Y%m%d%I:%M %p')
                    eastern_timezone = pytz.timezone('US/Eastern')
                    game_date = eastern_timezone.localize(game_date)
                    # convert to utc
                    game_date = game_date.astimezone(timezone.utc)
                    #skip old games (before today)
                    if game_date < timezone.now():
                        continue
                except ValueError:
                    # skip game if date is not valid
                    print(f'Invalid date: {game_time}')
                    continue
                # get home team and away team
                home_team = row[2]
                away_team = row[3]
                # clean up team names (remove spaces before and after)
                home_team = home_team.strip()
                away_team = away_team.strip()
                # get network
                network = row[4]
                # skip if no network
                if len(network) == 0:
                    continue
                network_link = None
                if row[5]:
                    network_link = row[5]
                # turn network into a list
                networks = network.split('|')
                # create teams
                home_team, created_home = Team.objects.get_or_create(name=home_team, league=league)
                away_team, created_away = Team.objects.get_or_create(name=away_team, league=league)
                # create game
                game, created_game = Game.objects.get_or_create(name=f"{home_team} vs {away_team}", league=league, sport=sport, time=game_date)
                counter += 1
                if created_game:
                    game.teams.add(home_team)
                    game.teams.add(away_team)
                    for network in networks:
                        print(f"{home_team} v {away_team} on {network}")
                        network, created = Network.objects.get_or_create(name=network)
                        game.networks.add(network)
                        if network_link:
                            watch_link, created = WatchLink.objects.get_or_create(label=network, url=network_link)
                            game.watch_links.add(watch_link)
                    game.save()
                    print(counter)
        return counter

    def ncaa_vball():
        CSV_DATA = NCAA_VBALL_FILE
        counter = 0
        # create a sport if it doesn't exist
        sport, created = Sport.objects.get_or_create(name='volleyball')
        # create a league if it doesn't exist
        league, created = League.objects.get_or_create(name='NCAA', sport=sport)

        # open csv file
        with open(CSV_DATA, 'r') as csv_file:
            # skip first line
            next(csv_file)
            # read csv file
            csv_reader = csv.reader(csv_file, delimiter=',')
            # loop through each row
            for row in csv_reader:
                # get date and time
                date = row[0]
                time = row[1]
                # handle when time is Noon
                if time == 'Noon':
                    time = '12:00 PM'
                game_time = date + time
                # convert to datetime (format is 202401117:00 PM)
                try:
                    game_date = datetime.datetime.strptime(game_time, '%Y%m%d%I:%M %p')
                    eastern_timezone = pytz.timezone('US/Eastern')
                    game_date = eastern_timezone.localize(game_date)
                    # convert to utc
                    game_date = game_date.astimezone(timezone.utc)
                    #skip old games (before today)
                    if game_date < timezone.now():
                        continue
                except ValueError:
                    # skip game if date is not valid
                    print(f'Invalid date: {game_time}')
                    continue

                # get home team and away team
                home_team = row[2]
                away_team = row[3]
                # clean up team names (remove spaces before and after)
                home_team = home_team.strip()
                away_team = away_team.strip()
                # get network
                network = row[4]
                # skip if no network
                if len(network) == 0:
                    continue
                network_link = None
                if row[5]:
                    network_link = row[5]
                # turn network into a list
                networks = network.split(',')
                # create teams
                home_team, created_home = Team.objects.get_or_create(name=home_team, league=league)
                away_team, created_away = Team.objects.get_or_create(name=away_team, league=league)
                # create game
                game, created_game = Game.objects.get_or_create(name=f"{home_team} vs {away_team}", league=league, sport=sport, time=game_date)
                counter += 1
                if created_game:
                    game.teams.add(home_team)
                    game.teams.add(away_team)
                    for network in networks:
                        print(f"{home_team} v {away_team} on {network}")
                        network, created = Network.objects.get_or_create(name=network)
                        game.networks.add(network)
                        if network_link:
                            watch_link, created = WatchLink.objects.get_or_create(label=network, url=network_link)
                            game.watch_links.add(watch_link)
                    game.save()
                    print(counter)
        return counter
   
    def us_soccer():
        counter = 0
        response = requests.get(US_SOCCER)
        json = response.json()
        for game in json:
            # get date and time
            date = game.get('date')
            
            # add timezone as UTC
            # if date dose not have a timezone, add UTC
            if date[-1] != 'Z':
                date = date + 'Z'
            date_format = "%Y-%m-%dT%H:%M:%SZ"
            game_date = datetime.datetime.strptime(date, date_format).replace(tzinfo=timezone.utc)
            game_date = game_date.astimezone(timezone.utc)      
            
            # get network
            networks = game.get('broadcastLinks', [])
            network_list = []
            watch_links = []
            for network in networks:
                network_name = network.get('imageAltText')
                if network_name:
                    network_list.append(network_name)
                    # create watch link
                    url = network.get('broadcastURLWeb')
                    print(url)
                    if url:
                        watch_link, created = WatchLink.objects.get_or_create(label=network_name, url=url)
                        watch_links.append(watch_link)
            # teams
            teams = game.get('contestants', [])
            home_team = None
            away_team = None
            for team in teams:
                if team.get('position') == 'home':
                    home_team = team.get('code')
                elif team.get('position') == 'away':
                    away_team = team.get('code')

            if home_team is None or away_team is None:
                continue
            print(home_team)
            print(away_team)
            # create sport
            sport, created = Sport.objects.get_or_create(name='soccer')
            # create league
            league, created = League.objects.get_or_create(name='US Soccer', sport=sport)
            # create teams
            home_team, created_home = Team.objects.get_or_create(name=home_team, league=league)
            away_team, created_away = Team.objects.get_or_create(name=away_team, league=league)
            # create game
            game, created_game = Game.objects.get_or_create(name=f"{home_team} vs {away_team}", league=league, sport=sport, time=game_date)
            counter += 1
            if created_game:
                game.teams.add(home_team)
                game.teams.add(away_team)
                for network in network_list:
                    network, created = Network.objects.get_or_create(name=network)
                    game.networks.add(network)
                for watch_link in watch_links:
                    game.watch_links.add(watch_link)
                game.save()
        return counter

    def pwhl():
        # https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

        cities = {
            'Toronto': 'America/Toronto',
            'Boston': 'America/New_York',
            'Minnesota': 'America/Chicago',
            'Ottawa': 'America/Toronto',
            'Montreal': 'America/Montreal',
            'New York': 'America/New_York',
        }
        counter = 0
        # set user agent to get around 403 error
        headers = {'User-Agent': 'Mozilla/5.0'}
        page = requests.get(PWHL_ENDPOINT, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")
        schedule_table = soup.find('table')
        if schedule_table:
            print('Found table')
            rows = schedule_table.find_all('tr')
            for row in rows[1:]:  # Skipping the header row
                # get cells
                cells = row.find_all("td")
                # skip if no cells
                if len(cells) == 0:
                    continue
                # get date
                date = cells[0].text.strip()
                # get time
                time = cells[1].text.strip()
                # get home team
                home_team = cells[2].text.strip()
                # get away team
                away_team = cells[3].text.strip()
                print(f"{date} {time} {home_team} vs {away_team}")
                # add new cities to cities
                if cities.get(home_team) is None:
                    continue
                utc_time = Command.convert_local_time_to_utc(f'{date} {time}', cities.get(home_team))
                # network
                network = 'YouTube'
                sport = 'hockey'
                league = 'PWHL'
                # create sport
                sport, created = Sport.objects.get_or_create(name=sport)
                # create league
                league, created = League.objects.get_or_create(name=league, sport=sport)
                # create teams
                home_team, created_home = Team.objects.get_or_create(name=home_team, league=league)
                away_team, created_away = Team.objects.get_or_create(name=away_team, league=league)
                # create game\
                try:
                    game, created_game = Game.objects.get_or_create(name=f"{home_team} vs {away_team}", league=league, sport=sport, time=utc_time)
                    # add teams to game
                    game.teams.add(home_team)
                    game.teams.add(away_team)
                    # add network to game
                    network, created = Network.objects.get_or_create(name=network)
                    game.networks.add(network)
                    game.save()
                    counter += 1
                except Exception as e:
                    print(f'Error creating game: {e}')
                    continues

        return counter        

    def fifa_network_lookup():
        """
        Create a map where the key is the match id and
        the value is a list of networks
        """
        USA_ID = 149
        response = requests.get(FIFA_NETWORK_LOOKUP)
        json = response.json()
        # json = Command.fifa_sample_fifa_watch()
        data = json.get('Results')
        match_map = {}
        if data and data[USA_ID] and data[USA_ID].get('IdCountry') == 'USA':
            # get list of matches
            matches = data[USA_ID].get('Matches')
            for match in matches:
                match_id = match.get('IdMatch')
                networks = match.get('Sources')
                clean_networks = []
                if networks:
                    for network in networks:
                        network_name = network.get('Name')
                        language = network.get('Language')
                        if language != 'English':
                            network_name = f'{network_name} ({language})'
                        if network_name:
                            # create network
                            network, created = Network.objects.get_or_create(name=network_name)
                            clean_networks.append(network)
                match_map[match_id] = clean_networks
        return match_map
       
    def fifa_sample_data():
        # get sample data from file
        with open('./games/data/sample-fifa.json') as json_file:
            # return data from json file
            return json.load(json_file)

    def fifa_sample_fifa_watch():
        # get sample data from file
        with open('./games/data/sample-fifa-watch.json') as json_file:
            # return data from json file
            return json.load(json_file)
    
    def make_tbd_team(letter):
        return {FIFA_TBA}-{letter}
    
    def fifa():
        counter = 0
        response = requests.get(FIFA_ENDPOINT)
        json = response.json()
        #json = Command.fifa_sample_data()
        matches = json.get('Results')
        match_map = Command.fifa_network_lookup()
        # create sport
        sport, created = Sport.objects.get_or_create(name='soccer')
        # create league
        league, created = League.objects.get_or_create(name='FIFA', sport=sport)
        for match in matches:
            home_team = match.get('Home')
            away_team = match.get('Away')

            if home_team is None:
                home_team = f'{FIFA_TBA}-A'
            else:
                home_team = home_team.get('ShortClubName')

            if away_team is None:
                away_team = f'{FIFA_TBA}-B'
            else:
                away_team = away_team.get('ShortClubName')


            home_team, created = Team.objects.get_or_create(name=home_team, league=league)
            away_team, created = Team.objects.get_or_create(name=away_team, league=league)
            match_id = match.get('IdMatch')
            networks = match_map.get(match_id)
            date = match.get('Date')      
            if date:
                # format is 2023-07-31T10:00:00Z
                game_date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                name = f"{FIFA_NAME_PREFIX} {home_team} vs {away_team}"
                game, created_game = Game.objects.get_or_create(name=name, league=league, sport=sport, time=game_date)

                if created_game:
                    game.teams.add(home_team)
                    game.teams.add(away_team)
                    for network in networks:
                        game.networks.add(network)
                    game.save()
                    counter += 1
        return counter
    
    def au():
        counter = 0
        # load data from file
        with open('./games/data/au_softball.json') as json_file:
            # return data from json file
            data = json.load(json_file)
            # create sport
            sport, created = Sport.objects.get_or_create(name='softball')
            # create league
            league, created = League.objects.get_or_create(name='Athletes Unlimited', sport=sport)
            
            for game in data:
                # get name and find teams based on team1 vs. team2
                # check for null netowrk
                if game.get('network') is None:
                    print('skipping game')
                    continue
                name = game['name']
                print(name)
                teams = name.split(' vs. ')
                team1 = teams[0]
                team2 = teams[1]
                
                # get date and time based on epoch
                date = game['date']
                # convert to date from string to int
                date = int(date)
                # convert to datetime
                date = datetime.datetime.fromtimestamp(date)
                # convert to utc
                date = date.astimezone(timezone.utc)

                # network
                network = game['network']
                # watch link
                watch_link = game['link']
                # create network
                network, created = Network.objects.get_or_create(name=network)
                # create watch link
                watch_link, created = WatchLink.objects.get_or_create(label=network, url=watch_link)

                # create teams
                team1, created = Team.objects.get_or_create(name=team1, league=league)
                team2, created = Team.objects.get_or_create(name=team2, league=league)
                # create game
                if watch_link:
                    game, created_game = Game.objects.get_or_create(name=name, time=date, league=league, sport=sport)
                    if created_game:
                        counter += 1
                        game.teams.add(team1)
                        game.teams.add(team2)
                        if network:
                            game.networks.add(network)
                        if watch_link:
                            game.watch_links.add(watch_link)
                        game.save()
        return counter

                

    def add_arguments(self, parser):
        parser.add_argument('--fresh_data', type=str, help='Delete all games, teams, leagues, networks, and sports before adding new data', default='False')
        parser.add_argument('--league', type=str, help='Add only league passed', default='')

    def handle(self, *args, **options):
        # get args
        FRESH_DATA = options['fresh_data']
        if FRESH_DATA:
            FRESH_DATA = str2bool(FRESH_DATA)
        # if fresh data is needed, delete all games, teams, leagues, networks, and sports
        if FRESH_DATA:
            Game.objects.all().delete()
            Team.objects.all().delete()
            League.objects.all().delete()
            Sport.objects.all().delete()
            Network.objects.all().delete()

        leagues = {
            'ncaa': ('NCAA', 'Successfully added {} NCAA games'),
            'ncaa_vball': ('ncaa_vball', 'Successfully added {} NCAA Volleyball games'),
            'wnba': ('WNBA', 'Successfully added {} WNBA games'),
            'pwhl': ('pwhl', 'Successfully added {} pwhl games'),
            'nwsl': ('NWSL', 'Successfully added {} NWSL games'),
            'fifa': ('FIFA', 'Successfully added {} FIFA games'),
            'au': ('AU', 'Successfully added {} softball games'),
            'us_soccer': ('us_soccer', 'Successfully added {} US Soccer games'),
        }

        league_name = options['league']
        if league_name:
            if league_name in leagues:
                league_data = leagues[league_name]
                try:
                    count = getattr(Command, league_data[0].lower())()
                    self.stdout.write(self.style.SUCCESS(league_data[1].format(count)))
                except Exception as e:
                    raise CommandError(f'Error adding games: {e}')
            else:
                raise CommandError(f'League {league_name} does not exist')
        else:
            # run all leagues
            for league_data in leagues.values():
                try:
                    count = getattr(Command, league_data[0].lower())()
                    self.stdout.write(self.style.SUCCESS(league_data[1].format(count)))
                except Exception as e:
                    raise CommandError(f'Error adding games: {e}')



