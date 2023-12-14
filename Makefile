start:
	python manage.py runserver

user:
	python manage.py createsuperuser

data:
	python manage.py add_games --fresh_data True

wnba:
	python manage.py add_games --fresh_data False --league wnba

nwsl:
	python manage.py add_games --fresh_data False --league nwsl

fifa:
	python manage.py add_games --fresh_data False --league fifa

us_soccer:
	python manage.py add_games --fresh_data False --league us_soccer

au:
	python manage.py add_games --fresh_data False --league au

ncaa_scrape:
	python manage.py ncaa_scrape --dry_run False

ncaa_data:
	python manage.py ncaa_data

ncaa:
	python manage.py add_games --fresh_data False --league ncaa

clean:
	python manage.py clean_games --all_games False 

clean_teams:
	python manage.py clean_teams

really_clean:
	python manage.py clean_games --all_games True

clean_fifa:
	python manage.py clean_games --all_games True --league FIFA

clean_wnba:
	python manage.py clean_games --all_games True --league WNBA

clean_nwsl:
	python manage.py clean_games --all_games True --league NWSL

clean_au:
	python manage.py clean_games --all_games True --league "Athletes Unlimited"

clean_ncaa:
	python manage.py clean_games --all_games True --league NCAA

clean_us_soccer:
	python manage.py clean_games --all_games True --league "US Soccer"

dep:
	python -m pip freeze > requirements.txt

scrape_au:
	scrapy runspider ./games/management/commands/au_scrape.py -o ./games/data/au_softball.json