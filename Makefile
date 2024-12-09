start:
	python manage.py runserver

user:
	python manage.py createsuperuser

data:
	python manage.py add_games --fresh_data True

wnba:
	python manage.py add_games --fresh_data False --league wnba

pwhl:
	python manage.py add_games --fresh_data False --league pwhl

nwsl:
	python manage.py add_games --fresh_data False --league nwsl

fifa:
	python manage.py add_games --fresh_data False --league fifa

us_soccer:
	python manage.py add_games --fresh_data False --league us_soccer

au:
	python manage.py add_games --fresh_data False --league au

au_scrape:
	python manage.py au_scrape

ncaa_scrape:
	python manage.py ncaa_scrape --dry_run False

ncaa_vball_scrape:
	python manage.py ncaa_volleyball_scrape --dry_run False


ncaa_data:
	python manage.py ncaa_data

ncaa_vball_data:
	python manage.py ncaa_volleyball_data

ncaa:
	python manage.py add_games --fresh_data False --league ncaa

ncaa_vball:
	python manage.py add_games --fresh_data False --league ncaa_vball

clean:
	python manage.py clean_games --all_games False 

clean_teams:
	python manage.py clean_teams

really_clean:
	python manage.py clean_games --all_games True --all_models True

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

clean_pwhl:
	python manage.py clean_games --all_games True --league PWHL

clean_us_soccer:
	python manage.py clean_games --all_games True --league "US Soccer"

dep:
	python -m pip freeze > requirements.txt

scrape_au:
	scrapy runspider ./games/management/commands/au_scrape.py -o ./games/data/au_softball.json

rank:
	python manage.py rank_teams
	
recover_nwsl:
	python manage.py recover_nwsl