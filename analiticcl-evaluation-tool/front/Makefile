all: help
tag = ga-analiticcl-evaluate-front

.PHONY: build docker-image start help push update-version with-versions without-versions

.make:
	mkdir -p .make

.make/.install: .make package.json tsconfig.json
	npx yarn install
	@touch .make/.install

.make/.build: .make .make/.install src/* public/* update-version
	npx yarn build
	@touch .make/.build

build: .make/.build

.make/.docker: .make docker/Dockerfile public/* src/* package.json
	docker build -t $(tag):latest -f docker/Dockerfile .
	docker tag $(tag):latest registry.diginfra.net/tt/$(tag):latest
	@touch .make/.docker

docker-image: .make/.docker prod-config

.make/.push: .make/.docker
	docker push registry.diginfra.net/tt/$(tag):latest
	@touch .make/.push

push: .make/.push

start: .make/.install
	npx yarn start

clean:
	rm -rf .make build

update-version:
	@echo "set version to `date +%Y.%m.%d`"
	@jq ".version=\"`date +%Y.%m.%d`\"" src/config.json > /tmp/config.json && mv /tmp/config.json src/

dev-config:
	@echo "set developmentMode to true"
	@jq ".developmentMode=true" src/config.json > /tmp/config.json && mv /tmp/config.json src/

prod-config:
	@echo "set developmentMode to false"
	@jq ".developmentMode=false" src/config.json > /tmp/config.json && mv /tmp/config.json src/

with-versions:
	@echo "enabled version menu"
	@jq ".versionSelector=true" src/config.json > /tmp/config.json && mv /tmp/config.json src/

without-versions:
	@echo "disabled version menu"
	@jq ".versionSelector=false" src/config.json > /tmp/config.json && mv /tmp/config.json src/


help:
	@echo "make-tools for $(tag)"
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  start           to run the app in development mode"
	@echo "  build           to build the app for deployment"
	@echo "  docker-image    to build the docker image of the app, running in nginx"
	@echo "  push            to push the docker image to registry.diginfra.net"
	@echo "  clean           to remove generated files"
	@echo "  update-version  to set the version to the current year.month.day"
	@echo "  dev-config      to use the development config"
	@echo "  prod-config     to use the production config"
