import re
import os
import csv
import datetime
import time
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


NCAA_FILE_DIR = './games/data/ncaa_volleyball/'
NCAA_DATA_DIR = './games/data/ncaa_data_volleyball/'

NCAA_FINAL = NCAA_DATA_DIR + 'final.csv'

class Command(BaseCommand):
    def strip_rank(team):
        # remove any number in front of team name
        name_without_numbers = re.sub(r'^\d+', '', team)
        # remove anything like #17
        name_without_numbers = re.sub(r'#\d+', '', name_without_numbers)
        # also remove any spaces left over
        name_without_numbers = name_without_numbers.strip()
        return name_without_numbers
    
    def get_ncaa_html(date_str):
        with open(f'./games/data/ncaa_volleyball/{date_str}.html') as html_file:
                page = html_file.read()
                html = BeautifulSoup(page, "html.parser")
        return html
                   
    def scrape_html(self):
        counter = 0
        all_games = []

        # get the files names in NCAA_FILE_DIR and strip the .html
        dates = [f[:-5] for f in os.listdir(NCAA_FILE_DIR) if os.path.isfile(os.path.join(NCAA_FILE_DIR, f))]
        
        for date in dates:
            # if file doesn't look like a date, skip
            if len(date) != 8:
                continue
            # get html
            html = Command.get_ncaa_html(date)
            # get games
            rows = html.find_all("tr", class_="Table__TR")
            for row in rows:
                # time .Table__TD--time Table__TD
                time = row.find("td", class_="Table__TD--time")
                # time is in cenral time, make it UTC
                if not time:
                    continue
                time = time.get_text()
                names = row.find_all("td", class_="Table__TD--name")
                # team names
                names = names[0].get_text()
                # split team names
                teams = names.split(' vs. ')
                if len(teams) != 2:
                    continue
                home_team = teams[0]
                away_team = teams[1]
                # strip rank
                home_team = Command.strip_rank(home_team)
                away_team = Command.strip_rank(away_team)
                # network Table__TD--logo Table__TD
                network = row.find("td", class_="Table__TD--logo")
                network = network.find("img")
                network = network['alt']
                # all cap network
                network = network.upper()
                # get the network link
                network_link = None
                network_a = row.find("a", class_="AnchorLink")
                if network_a:
                    network_link = network_a['href']
                    domain = 'https://www.espn.com'
                    network_link = domain + network_link
                # append to all_games
                all_games.append([date, time, home_team, away_team, network, network_link])
                counter += 1
        # write to csv
        with open(NCAA_FINAL, mode='w') as file:
            writer = csv.writer(file)
            writer.writerow(['date', 'time', 'home_team', 'away_team', 'network', 'network_link'])
            for game in all_games:
                writer.writerow(game)
        




                
            
                

    
    def handle(self, *args, **options):
        Command.scrape_html(self)
        print('Done')

