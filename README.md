## Деплой приложения на PaaS (DevOps)

[![Actions Status](https://github.com/mikitasazan/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/mikitasazan/devops-engineer-from-scratch-project-313/actions)

Учебный DevOps-проект на Python: сервис сокращения ссылок с CRUD-бэкендом,
Docker-образом, Nginx и деплоем на PaaS.

## Архитектура

- Flask-бэкенд с SQLModel и PostgreSQL;
- frontend подключается как npm-зависимость Hexlet;
- Nginx проксирует API и отдаёт собранную статику;
- Render запускает контейнер из `Dockerfile`.

## Доступный стенд

Приложение доступно по адресу:

https://devops-engineer-from-scratch-project-313-1rpc.onrender.com/

Адрес может измениться после пересоздания приложения. Перед проверкой
используйте актуальный URL из настроек Render.

## Требования

- Python 3.14+;
- Node.js и npm;
- Docker;
- `uv` или `pip`.

## Установка и команды

```bash
make install
make start
make lint
make test
```

Backend запускается на `http://127.0.0.1:8080`. Для отдельной сборки образа:

```bash
docker build -t paas-deployment:local .
docker run --rm -p 8080:8080 paas-deployment:local
```

Переменная `API_URL` задаёт адрес API для frontend. Команды деплоя и проверок
остаются в GitHub Actions и настройках PaaS-стенда.
