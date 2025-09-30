ARG NODE_VERSION=24

FROM docker.io/node:$NODE_VERSION

RUN apt-get update

RUN npm install -g npm

WORKDIR /app
COPY package.json package-lock.json /app/
RUN npm install

COPY . /app
