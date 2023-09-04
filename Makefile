SHELL := /bin/bash
LOCAL_COMPOSE_FILE := infra/dev/docker-compose.local.yaml
REDIS_PORT := 6379
REDIS_CONTAINER := $(shell docker ps -q -f name=redis-server)
CELERY_APP_PATH := webresource_watchdog.celery_app

COLOR_RESET = \033[0m
COLOR_GREEN = \033[32m
COLOR_YELLOW = \033[33m
COLOR_WHITE = \033[00m

.DEFAULT_GOAL := help

.PHONY: help
help:  # Show help
	@echo -e "$(COLOR_GREEN)Makefile help:"
	@grep -E '^[a-zA-Z0-9 -]+:.*#'  Makefile | sort | while read -r l; do printf "$(COLOR_GREEN)-$$(echo $$l | cut -f 1 -d':'):$(COLOR_WHITE)$$(echo $$l | cut -f 2- -d'#')\n"; done

.PHONY: makemigrations
makemigrations: # Make migrations
	@echo -e "$(COLOR_YELLOW)Making migrations...$(COLOR_RESET)"
	@until poetry run flask db migrate; do \
	  echo -e "$(COLOR_YELLOW)Waiting migrations to be created...$(COLOR_RESET)"; \
	  sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Migrations created$(COLOR_RESET)"

.PHONY: migrate
migrate: # Start migrations
	@echo -e "$(COLOR_YELLOW)Starting migrations...$(COLOR_RESET)"
	@until poetry run flask db upgrade; do \
	  echo -e "$(COLOR_YELLOW)Waiting migrations to be committed...$(COLOR_RESET)"; \
	  sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Migrations committed$(COLOR_RESET)"

.PHONY: run-flask
run-flask:  # Run Flask app
	@echo -e "$(COLOR_YELLOW)Starting flask app...$(COLOR_RESET)"
	@until poetry run flask run; do \
	  echo -e "$(COLOR_YELLOW)Waiting flask app to be started...$(COLOR_RESET)"; \
	  sleep 5 ;\
	done
	@sleep 3 ;
	@echo -e "$(COLOR_GREEN)Flask app started$(COLOR_RESET)"

.PHONY: start
start: # Run Application
	@if command -v docker &> /dev/null; then \
        docker-compose -f ./infra/docker-compose.yaml pull && \
		docker-compose -f ./infra/docker-compose.yaml up -d; \
    else \
        echo "Docker is not installed"; \
    fi
