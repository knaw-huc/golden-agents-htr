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
FROM nginx:latest

COPY --from=build /work/build /usr/share/nginx/html
