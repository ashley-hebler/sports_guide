start:
	python manage.py runserver

clean:
	echo "yes" | python manage.py flush

user:
	python manage.py createsuperuser

data:
	python manage.py add_games fresh_data=True

debug:
	python manage.py add_games fresh_data=False

wnba:
	python manage.py add_games fresh_data=True --league wnba

nwsl:
	python manage.py add_games fresh_data=False --league nwsl
