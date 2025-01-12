# command to write html files
# python manage.py ncaa_scrape
import os
from django.core.management.base import BaseCommand, CommandError
import datetime
import requests
from time import sleep
from bs4 import BeautifulSoup
from .utils import str2bool


NCAA_ENDPOINT = 'https://www.espn.com/watch/schedule/_/type/upcoming/categoryId/be9385dc-c518-3a55-9197-ec47a9e0e7f6/startDate/'


class Command(BaseCommand):
    def espn(dry_run=False):
        file_dir = './games/data/ncaa_volleyball/'
        counter = 0
        
        # date format is YYYYMMDD
        season_start = datetime.date(2024, 12, 13)
        #convert to string
        season_start_str = season_start.strftime('%Y%m%d')
        
        dates = []
        if dry_run:
            days = 1
        else:
            days = 162
        for i in range(days):
            date = season_start + datetime.timedelta(days=i)
            dates.append(date.strftime('%Y%m%d'))
        for date in dates:
            page = requests.get(NCAA_ENDPOINT + date, headers={'User-Agent': 'Mozilla/5.0'})
            if page.status_code != 200:
                print(page.status_code)
                print('Error getting page: ' + NCAA_ENDPOINT + date)
                # stop if page not found
                break
            html = BeautifulSoup(page.content, "html.parser")
            # write html to file
            file_name = date + '.html'
            file_path = file_dir + file_name
            with open(file_path, 'w') as file:
                file.write(str(html))
                print(f'Wrote {file_name}')
                counter += 1
            sleep(3)

        print(f'Wrote {counter} files to {file_dir}')

    def add_arguments(self, parser):
        parser.add_argument('--dry_run', type=str, help='Dry run', default='False')
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            dry_run = str2bool(dry_run)
        
        Command.espn(dry_run=dry_run)
      
