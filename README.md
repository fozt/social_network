## Run project using Docker compose
```sh
docker-compose up --build
```

## Setup database with initial data
```sh
docker exec -it fastapi_tg python app/db/session.py
```

## Linters

```sh
cd social
poetry run black .
poetry run isort --sp pyproject.toml .
```
