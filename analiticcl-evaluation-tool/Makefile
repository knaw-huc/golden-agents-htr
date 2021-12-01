all: help

.PHONY: build docker-image start help push

.make/:
	mkdir -p .make

.make/.install: .make package.json tsconfig.json
	yarn install
	@touch .make/.install

.make/.build: .make .make/.install src/* public/*
	yarn build
	@touch .make/.build

build: .make/.build

.make/.docker: .make docker/Dockerfile public/* src/* package.json
	docker build -t ga-analiticcl-evaluate:latest -f docker/Dockerfile .
	@touch .make/.docker

docker-image: .make/.docker

.make/.push: .make docker-image
	docker tag ga-analiticcl-evaluate:latest registry.diginfra.net/tt/ga-analiticcl-evaluate:latest
	docker push registry.diginfra.net/tt/ga-analiticcl-evaluate:latest
	@touch .make/.push

push: .make/.push

start:
	yarn start

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  build           to build the app for deployment"
	@echo "  start           to run the app in development mode"
	@echo "  docker-image    to build the docker image of the app, running in nginx"
	@echo "  push    		 to push the docker image to registry.diginfra.net"
