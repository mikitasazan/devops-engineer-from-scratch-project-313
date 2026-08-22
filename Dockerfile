# Собираем фронтовый образ
FROM node:20-alpine AS front-build

WORKDIR /front

COPY package.json package-lock.json ./

RUN npm ci

FROM python:3.14.3-alpine3.23 AS runtime-build

WORKDIR /app

RUN apk add --no-cache bash

# Инициализируем nginx
RUN apk add --no-cache nginx
COPY deploy/default.conf /etc/nginx/http.d/default.conf

# Устанавливаем в uv из офицального образа
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml /app/

RUN uv sync --extra dev

COPY /src ./src

#Копируем из фронтового образа скаченынй пакет с фронтовым приложением
COPY --from=front-build /front/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. ./public/

EXPOSE 80

# инициализируем entrypoint.sh
COPY /deploy/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
