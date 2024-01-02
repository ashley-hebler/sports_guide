from django.core.management.base import BaseCommand, CommandError
 
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import json

# scrape big east schedule
BIG_EAST_ENDPOINT = 'https://www.bigeast.com/services/responsive-calendar.ashx?start=Mon+Jan+01+2024&end=2024-03-03+23:59:59&sport_id=14&school_id=0'

SAMPLE_JSON = './games/data/sample-big-east.json'



class Command(BaseCommand):

    def handle(self, *args, **options):
        file_dir = './games/data/ncaa_conf_bigeast.csv'
        counter = 0

        # Open a CSV file for writing
        with open(file_dir, 'w', newline='') as csvfile:
            # Create a CSV writer object
            csv_writer = csv.writer(csvfile)

            # Write header row
            csv_writer.writerow(['Date','Time','Home Team','Away','Network'])
        
            # page = requests.get(BIG_EAST_ENDPOINT, headers={'User-Agent': 'Mozilla/5.0'})
            # if page.status_code != 200:
            #     print(page.status_code)
            #     print('Error getting page: ' + BIG_EAST_ENDPOINT)
            # if page.status_code == 200:
            #     # parse json
            #     json_data = page.json()

            # get sample json
            with open(SAMPLE_JSON) as json_file:
                json_data = json.load(json_file)

            for game in json_data:
                utc_date = game['date_utc']
                # date sample "2024-01-03T11:00:00"
                date = utc_date.split('T')[0]
                # strip hyphens
                date = date.replace('-', '')
                time = game['time']
                # strip period in AM/PM
                time = time.replace('.', '')

                home_team = game['school'].get('title')
                away_team = game['opponent'].get('title')
                

                media = game['media']
                networks = []
                if media:
                    tv = media.get('tv')
                    if tv:
                        networks.append(tv)
                    video = media.get('video')
                    if video:
                        video = video.get('title')
                        networks.append(video)
                if networks:
                    networks = ', '.join(networks)
                
                # Write row
                csv_writer.writerow([date, time, home_team, away_team, networks])
                
            
            

    
                

                    
    