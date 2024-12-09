from django.core.management.base import BaseCommand, CommandError


from datetime import datetime
from django.utils import timezone
import requests
from bs4 import BeautifulSoup

from games.models import Game, League, Team, Network
from .utils import str2bool

class Command(BaseCommand):
    """
    Delete games from a certain league or all games from past
    """
    help = 'Rank teams in a league'

    def rank_wbb(self):
        AP_RANKINGS = 'https://www.espn.com/womens-college-basketball/rankings'
        page = requests.get(AP_RANKINGS, headers={'User-Agent': 'Mozilla/5.0'})
        if page.status_code != 200:
            print(page.status_code)
            print('Error getting page: ' + AP_RANKINGS)
            return
        html = BeautifulSoup(page.content, "html.parser")
        # find the table
        table = html.find_all('table')[0]
        # find the rows
        rows = table.find_all('tr')
        # skip the header
        rows = rows[1:]
        found_teams = []
        for row in rows:
            # find the columns
            cols = row.find_all('td')
            # get the team name
            team_name_col = cols[1]
            # find abbr tag
            abbr = team_name_col.find_all('abbr')
            # get title of abbr tag
            team_name = abbr[0]['title']
            # get the rank
            try:
                rank = int(cols[0].text)
                print(f'Ranked {team_name} at {rank}')
                found_teams.append((team_name, rank))
            except ValueError:
                print(f'Could not rank {team_name}')
        # update the teams
        # get all teams in the league
        #get id of ncaa basketball
        leagues = League.objects.filter(name='NCAA')
        league_id = ''
        for league in leagues:
            sport = league.sport
            league_id = league.id
        teams = Team.objects.filter(league=league_id)
        print(teams)
        for team in teams:
            # remove all ranks
            if team.rank:
                team.rank = None
                team.save()
                print(f'Removed rank from {team.name}')
        for team in teams:
            # if team name is in the list of found teams
            for found_team in found_teams:
                if team.name in found_team:
                    team.rank = found_team[1]
                    team.save()
                    print(f'Updated {team.name} to rank {team.rank}')
                    break

    def rank_vb(self):
        AP_RANKINGS = 'https://www.ncaa.com/rankings/volleyball-women/d1/avca-rankings'
        page = requests.get(AP_RANKINGS, headers={'User-Agent': 'Mozilla/5.0'})
        if page.status_code != 200:
            print(page.status_code)
            print('Error getting page: ' + AP_RANKINGS)
            return
        html = BeautifulSoup(page.content, "html.parser")
        # find the table
        table = html.find_all('table')[0]
        # find the rows
        rows = table.find_all('tr')
        # skip the header
        rows = rows[1:]
        found_teams = []
        for row in rows:
            # find the columns
            cols = row.find_all('td')
            # get the team name
            team_name = cols[1].text
            # remove the parenthetical
            team_name = team_name.split('(')[0].strip()
            # get the rank
            try:
                rank = int(cols[0].text)
                print(f'Ranked {team_name} at {rank}')
                found_teams.append((team_name, rank))
            except ValueError:
                print(f'Could not rank {team_name}')
        # update the teams
        # get all teams in the league
        #get id of ncaa basketball
        leagues = League.objects.filter(name='NCAA')
        league_id = ''
        for league in leagues:
            sport = league.sport
            if sport.name == 'volleyball':
                league_id = league.id
            print(league_id)    
            teams = Team.objects.filter(league=69)
            print(teams)
            for team in teams:
                # remove all ranks
                if team.rank:
                    team.rank = None
                    team.save()
                    print(f'Removed rank from {team.name}')
            for team in teams:
                # if team name is in the list of found teams
                for found_team in found_teams:
                    if team.name in found_team:
                        team.rank = found_team[1]
                        team.save()
                        print(f'Updated {team.name} to rank {team.rank}')
                        break
           
    
    def handle(self, *args, **options):
        self.rank_vb()


