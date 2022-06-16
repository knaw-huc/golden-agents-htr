FROM alpine:3.16
MAINTAINER Maarten van Gompel <proycon@anaproy.nl>
LABEL description="Development environment for Golden Agents experiments"

RUN apk update && apk add python3 py3-pip py3-xmltodict py3-sparqlwrapper py3-numpy py3-scipy py3-dateutil py3-tabulate cargo jq ucto
RUN cargo install --root /usr analiticcl
RUN cargo install --root /usr lexmatch
RUN cargo install --root /usr sesdiff
RUN pip install analiticcl
RUN pip install dataclasses_json
RUN mkdir -p /data /tmp/golden-agents-ner
COPY package/ /tmp/golden-agents-ner
RUN cd /tmp/golden-agents-ner && pip install .
WORKDIR /work
CMD /bin/ash -l
