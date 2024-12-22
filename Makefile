CURDIR := $(shell pwd)
export COMPOSE_PROJECT_PATH=$(CURDIR)

all:
	@docker compose up --build -d

stop:
	@docker compose down

purge:
	@docker compose down -v

push:
	@ find backend/ -type f -name "00*" -delete

re: stop all

rebuild: purge all

.PHONY: all stop push re rebuild purge