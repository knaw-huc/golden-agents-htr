all: help
tag = ga-analiticcl-evaluate-front

.PHONY: build docker-image start help push

.make:
	mkdir -p .make

.make/.install: .make package.json tsconfig.json
	npx yarn install
	@touch .make/.install

.make/.build: .make .make/.install src/* public/*
	echo '{"version":"'$(date  +%Y.%m.%d)'"}' > src/config.json
	npx yarn build
	@touch .make/.build

build: .make/.build

.make/.docker: .make docker/Dockerfile public/* src/* package.json
	docker build -t $(tag):latest -f docker/Dockerfile .
	docker tag $(tag):latest registry.diginfra.net/tt/$(tag):latest
	@touch .make/.docker

docker-image: .make/.docker

.make/.push: .make/.docker
	docker push registry.diginfra.net/tt/$(tag):latest
	@touch .make/.push

push: .make/.push

start:
	npx yarn start

clean:
	rm -rf .make build

help:
	@echo "make-tools for $(tag)"
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  build           to build the app for deployment"
	@echo "  start           to run the app in development mode"
	@echo "  docker-image    to build the docker image of the app, running in nginx"
	@echo "  push            to push the docker image to registry.diginfra.net"
	@echo "  clean           to remove generated files"
