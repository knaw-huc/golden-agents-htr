# usage:
#   docker build -t ga-analiticcl-evaluation -f docker/Dockerfile .
#   docker run -p8888:80 ga-analiticcl-evaluation

# build
FROM node:12 AS build

WORKDIR /work
COPY package.json ./
COPY tsconfig.json ./
COPY public public
COPY src src
RUN yarn install
RUN yarn build

# run
FROM nginx:1.17.5-alpine

# install a8m/envsubst (used in cmd.sh)
RUN apk update &&\
	apk add curl &&\
	curl -L https://github.com/a8m/envsubst/releases/download/v1.2.0/envsubst-`uname -s`-`uname -m` -o envsubst && \
	chmod +x envsubst && \
	mv envsubst /usr/local/bin

COPY docker/nginx.tpl.conf /tmp/nginx.conf.tpl
COPY --from=build /work/build /usr/share/nginx/html
COPY docker/cmd.sh cmd.sh

CMD "./cmd.sh"