import re
import os
import csv
import datetime
import time
from bs4 import BeautifulSoup

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone


NCAA_FILE_DIR = './games/data/ncaa/'
NCAA_DATA_DIR = './games/data/ncaa_data/'
NCAA_STEP_1a = './games/data/ncaa_conf_bigeast.csv'
NCAA_STEP_1b ='./games/data/ncaa_conf_pdfs.csv'
NCAA_STEP_2 = NCAA_DATA_DIR + 'ncaa-conf.csv'
NCAA_STEP_3 = NCAA_DATA_DIR + 'ncaa-espn.csv'
NCAA_STEP_4 = NCAA_DATA_DIR + 'ncaa-espn-conf.csv'

NCAA_FINAL = NCAA_DATA_DIR + 'final.csv'

class Command(BaseCommand):
    def strip_rank(team):
        # remove any number in front of team name
        name_without_numbers = re.sub(r'^\d+', '', team)
        return name_without_numbers
    
    def get_ncaa_html(date_str):
        with open(f'./games/data/ncaa/{date_str}.html') as html_file:
                page = html_file.read()
                html = BeautifulSoup(page, "html.parser")
        return html

    def dedupe_games(games_a, games_b):
        merged_games = {}
        
        # Add games from games_a to the merged dictionary
        for game in games_a:
            key = (game['home_team'], game['away_team'], game['date'])
            merged_games[key] = game

        # Add games from games_b to the merged dictionary, excluding duplicates
        for game in games_b:
            key = (game['home_team'], game['away_team'], game['date'])
            if key not in merged_games:
                merged_games[key] = game

        # Convert the merged dictionary back to a list
        deduped_games = list(merged_games.values())
        return deduped_games
    
    def step_1(self):
        month_dict = {
            'October': '10',
            'November': '11',
            'December': '12',
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
        }
        games_a = []
        games_b = []
        # Read the data from a CSV file
        with open(NCAA_STEP_1a, newline='') as csvfile_old_a:
            reader = csv.DictReader(csvfile_old_a)
            for row in reader:
                date = row['Date']
                time = row['Time']
                home_team = row['Home Team']
                away_team = row['Away']
                network = row['Network']
                if network:
                    games_a.append({
                        'date': date,
                        'time': time,
                        'home_team': home_team,
                        'away_team': away_team,
                        'network': network,
                    })
       
        with open(NCAA_STEP_1b, newline='') as csvfile_old_b:
            reader = csv.DictReader(csvfile_old_b)
            for row in reader:
                date = row['Date']
                time = row['Time']
                home_team = row['Home Team']
                away_team = row['Away']
                network = row['Network']

                # month is first word in date
                month = date.split(' ')[0]
                # day is second word in date
                day = date.split(' ')[1]

                #convert month to number
                month = month_dict[month]

                # add leading zero to day if needed
                if len(day) == 1:
                    day = f"0{day}"
                # make date MMDD (add leading zero if needed and remove space)
                date = date.replace(' ', '')
                
                # if nov or dec, year is 2023
                if month in ['10', '11', '12']:
                    year = '2023'
                else:
                    year = '2024'
                # make date YYYYMMDD
                date = f"{year}{month}{day}"

                # Combine date and time into a single key
                date_time = f"{date},{time}"

                # if network is empty, skip
                if network == '':
                    continue
                
                games_b.append({
                    'date': date,
                    'time': time,
                    'home_team': home_team,
                    'away_team': away_team,
                    'network': network,
                })
        
        # dedupe games_a and games_b
        games = Command.dedupe_games(games_a, games_b)
        # Write the deduplicated data to a new CSV file
        with open(NCAA_STEP_2, 'w', newline='') as output_csv:
            writer = csv.writer(output_csv)
            writer.writerow(['Date', 'Time', 'Home Team', 'Away', 'Network'])
            for game in games:
                writer.writerow(game.values())
                   
    def step_2(self):
        counter = 0
        # add heading to csv file
        with open(NCAA_STEP_3, 'w') as csv_file:
            csv_file.write('Date,Time,Home Team,Away,Network\n')

        # get the files names in NCAA_FILE_DIR and strip the .html
        dates = [f[:-5] for f in os.listdir(NCAA_FILE_DIR) if os.path.isfile(os.path.join(NCAA_FILE_DIR, f))]
        
        for date in dates:
            # if file doesn't look like a date, skip
            if len(date) != 8:
                continue
            # get html
            html = Command.get_ncaa_html(date)
            rows = html.find_all("tr", class_="Table__TR")
            for row in rows:
                # find team
                teams = row.find_all("span", class_="Table__Team")
                team_names = [Command.strip_rank(team.text) for team in teams]
                game_name = ' vs '.join(team_names)
                # create an html file for row  
                # with open(f'./games/data/ncaa-{game_name}-row.html', 'w') as html_file:
                #     html_file.write(str(row))
                network_selector = row.select_one(".broadcast__col img")
                network_selector_2 = row.select_one(".network-name")
                network_name = None
                if network_selector:
                    network_name = network_selector.attrs['alt']
                elif network_selector_2:
                    # try to find text
                    network_name = network_selector_2.get_text()
                else:
                    continue
                date_selector = row.select_one(".date__col")
                if date_selector:
                    time_string = date_selector.text
                    if time_string == 'TBD':
                        # skip game
                        continue
                    if time_string == 'LIVE':
                        # set start time to current time
                        start_time = datetime.datetime.now(tz=timezone.utc)
                    else:
                        # timezone is eastern
                        start_time_str = date + time_string + ' -0500'
                        start_time = datetime.datetime.strptime(start_time_str, '%Y%m%d%I:%M %p %z')
                        start_time = start_time.astimezone(timezone.utc)
                else:
                    continue

                # create csv file date, time, home, away, network
                with open(NCAA_STEP_3, 'a') as csv_file:
                    csv_file.write(f'{date},{time_string},{(team_names[0])},{team_names[1]},{network_name}\n')

    def step_3(self):
        # Define the paths to the two CSV files
        file1 = NCAA_STEP_2
        file2 = NCAA_STEP_3

        # Define the path for the merged CSV file
        merged_file = NCAA_STEP_4
        final_file = NCAA_FINAL

        # Initialize lists to store data from both files
        data_from_file1 = []
        data_from_file2 = []

        # Read data from the first CSV file
        with open(file1, newline='') as csvfile1:
            reader1 = csv.DictReader(csvfile1)
            data_from_file1 = [row for row in reader1]

        # Read data from the second CSV file
        with open(file2, newline='') as csvfile2:
            reader2 = csv.DictReader(csvfile2)
            data_from_file2 = [row for row in reader2]

        # Merge data from both files
        merged_data = data_from_file1 + data_from_file2

        # Write the merged data to a new CSV file
        with open(merged_file, 'w', newline='') as merged_csvfile:
            fieldnames = merged_data[0].keys()
            writer = csv.DictWriter(merged_csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(merged_data)



        # now dedupe the merged file

        # Read the CSV data into a list
        data = []
        with open(merged_file, 'r') as csv_file:
            reader = csv.reader(csv_file)
            next(reader)  # Skip the header row
            data = [row for row in reader]

        # Create a dictionary to store unique rows based on the combination of teams and dates
        deduplicated_data = {}

        for row in data:
            date, _, home_team, away_team, _ = row
            team_combo = (home_team, away_team, date)

            if team_combo not in deduplicated_data:
                deduplicated_data[team_combo] = row

        # Write the deduplicated data to a new CSV file
        with open(final_file, 'w', newline='') as output_csv:
            writer = csv.writer(output_csv)
            writer.writerow(['Date', 'Time', 'Home Team', 'Away', 'Network'])
            for row in deduplicated_data.values():
                writer.writerow(row)
            print(f'All data has been saved to {final_file}')
    
    def handle(self, *args, **options):
        Command.step_1(self)
        Command.step_2(self)
        Command.step_3(self)
