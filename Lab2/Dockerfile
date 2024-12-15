FROM node:20.17.0

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

EXPOSE  10000

CMD [ "npm","start" ]

