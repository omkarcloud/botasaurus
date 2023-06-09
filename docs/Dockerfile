FROM node:18-alpine

WORKDIR /app
COPY package.json .
RUN npm run clean
COPY . .
RUN npm run build
EXPOSE 3000
CMD npm run serve  --  --port 3000 --host 0.0.0.0