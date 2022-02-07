all: help
tag = ga-analiticcl-evaluate-back

.PHONY: docker-image start help push install

.make:
	mkdir -p .make

.make/.install: .make requirements.txt
	pip install -r requirements.txt
	@touch .make/.install

install: .make/.install

.make/.docker: .make Dockerfile data/ main.py requirements.txt
	docker build -t $(tag):latest .
	@touch .make/.docker

docker-image: .make/.docker

.make/.push: .make/.docker
	docker tag $(tag):latest registry.diginfra.net/tt/$(tag):latest
	docker push registry.diginfra.net/tt/$(tag):latest
	@touch .make/.push

push: .make/.push

start:
	python main.py

clean:
	rm -rf .make

help:
	@echo "make-tools for $(tag)"
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  docker-image    to build the docker image of the app, running in nginx"
	@echo "  push            to push the docker image to registry.diginfra.net"
	@echo "  install         to install the dependencies"
	@echo "  start           to start the app"
	@echo "  clean           to remove generated files"
