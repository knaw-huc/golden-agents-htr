FROM alpine:edge
MAINTAINER Maarten van Gompel <proycon@anaproy.nl>
LABEL description="Development environment for Golden Agents experiments"

RUN apk update && apk add python3 py3-pip py3-xmltodict py3-sparqlwrapper py3-numpy py3-scipy py3-dateutil cargo jq ucto
RUN cargo install --root /usr analiticcl
RUN cargo install --root /usr lexmatch
RUN cargo install --root /usr sesdiff
RUN pip install analiticcl
RUN mkdir -p /data /tmp/golden-agents-ner
COPY package/ /tmp/golden-agents-ner
RUN cd /tmp/golden-agents-ner && pip install .
WORKDIR /data
CMD /bin/ash -l
