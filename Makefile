start:
	python manage.py runserver

clean:
	echo "yes" | python manage.py flush
	python manage.py createsuperuser

user:
	python manage.py createsuperuser

data:
	python manage.py add_games fresh_data=True

debug:
	python manage.py add_games fresh_data=False