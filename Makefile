# Makefile
include .env

reset-migrations:
	find sportsclub/ -path "*/migrations/*.py" -not -name "__init__.py" -delete
	find sportsclub/ -path "*/migrations/*.pyc" -delete

reset-db:
	PGPASSWORD=$(POSTGRES_PASSWORD) psql -h 127.0.0.1 -p 5432 -U $(POSTGRES_USER) -d postgres -c "DROP DATABASE IF EXISTS $(POSTGRES_DB);"
	PGPASSWORD=$(POSTGRES_PASSWORD) psql -h 127.0.0.1 -p 5432 -U $(POSTGRES_USER) -d postgres -c "CREATE DATABASE $(POSTGRES_DB);"

reset-all: reset-db reset-migrations
	cd sportsclub && python manage.py makemigrations core
	cd sportsclub && python manage.py makemigrations inventory
	cd sportsclub && python manage.py makemigrations people
	cd sportsclub && python manage.py makemigrations scheduling
	cd sportsclub && python manage.py migrate

load-fixtures:
	cd sportsclub && python manage.py loaddata \
		core/fixtures/addresses.json \
		inventory/fixtures/venues.json \
		people/fixtures/coaches.json \
		people/fixtures/athletes.json \
		scheduling/fixtures/seasons.json \
		scheduling/fixtures/competitions.json \
		scheduling/fixtures/trainings.json

create-superuser:
	cd sportsclub && python manage.py createsuperuser \
		--username admin --email root@localhost
