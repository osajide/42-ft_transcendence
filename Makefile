all:
	@docker compose -f ./setup/docker/docker-compose.yml up --build -d

stop:
	@docker compose -f ./setup/docker/docker-compose.yml down

push:
	@find backend/ -type f -name "00*" -delete

re: stop all

.PHONY: all stop push re