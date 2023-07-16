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

clean:
	python manage.py clean_games --all_games False 

really_clean:
	python manage.py clean_games --all_games True

clean_fifa:
	python manage.py clean_games --all_games True --league FIFA

clean_wnba:
	python manage.py clean_games --all_games True --league WNBA

clean_nwsl:
	python manage.py clean_games --all_games True --league NWSL

make dep:
	python -m pip freeze > requirements.txt