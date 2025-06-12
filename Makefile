# Makefile for MQTT RTLS API

.PHONY: help build up down logs clean test restart status

help:
	@echo "MQTT RTLS API - Docker Commands"
	@echo "==============================="
	@echo "make build    - Build Docker images"
	@echo "make up       - Start all services"
	@echo "make down     - Stop all services"
	@echo "make logs     - View logs from all services"
	@echo "make clean    - Remove containers and volumes"
	@echo "make test     - Run tests in Docker"
	@echo "make restart  - Restart all services"
	@echo "make status   - Show status of all services"
	@echo "make shell    - Open shell in publisher container"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services starting..."
	@echo "MQTT Broker: localhost:1883"
	@echo "MQTT WebSocket: localhost:9001"
	@echo "MQTT Explorer: http://localhost:4000"
	@sleep 3
	@make status

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-publisher:
	docker-compose logs -f rtls-publisher

logs-subscriber:
	docker-compose logs -f rtls-subscriber

logs-broker:
	docker-compose logs -f mosquitto

clean:
	docker-compose down -v
	rm -rf mosquitto/data/*
	rm -rf mosquitto/log/*

test:
	docker-compose run --rm rtls-publisher pytest tests/

restart:
	docker-compose restart

status:
	@echo "Service Status:"
	@echo "==============="
	@docker-compose ps

shell:
	docker-compose exec rtls-publisher /bin/bash

# Development commands
dev-build:
	docker-compose build --no-cache

dev-up:
	docker-compose up

# Single service commands
broker-only:
	docker-compose up -d mosquitto

publisher-only:
	docker-compose up -d rtls-publisher

subscriber-only:
	docker-compose up -d rtls-subscriber