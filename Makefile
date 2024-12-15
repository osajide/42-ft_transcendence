all:
	@docker compose -f ./setup/docker/docker-compose.yml up --build -d

stop:
	@docker compose -f ./setup/docker/docker-compose.yml down

purge:
	@docker compose -f ./setup/docker/docker-compose.yml down -v

push:
	@find backend/ -type f -name "00*" -delete

re: stop all

rebuild: purge all

.PHONY: all stop push re rebuild purge