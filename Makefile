all:
	@python3 -m venv ../pong_venv

start: push
	@pip install -r requirements.txt
	@docker compose -f ./setup/docker/docker-compose.yml up --build -d
	@python backend/manage.py makemigrations
	@python backend/manage.py migrate
	@python backend/manage.py runserver 0.0.0.0:8000

stop:
	@docker compose -f ./setup/docker/docker-compose.yml down

re: stop all

push:
	@find backend/ -type f -name "00*" -delete