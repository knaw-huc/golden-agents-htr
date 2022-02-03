# Golden Agents NER pipeline on HTR output

This repository contains the pipeline for Named Entity Recognition on HTR output, powered
by [analiticcl](https://github.com/proycon/analiticcl).

## Development environment

The Docker file contains a development environment with all dependencies pre-installed.

To build it, first clone this repository and then run:

``
$ docker build --tag golden-agents-htr:latest .
``

To run it, mounting the current directory holding this repository into the container:

``
$ docker run -t -i -v "$(realpath .):/data" golden-agents-htr:latest
``





