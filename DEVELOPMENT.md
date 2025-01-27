# Development

### Build docker image
```bash
docker build -t sqlalchemy-fake-model .
```

### Run docker container in interactive mode
```bash
docker compose up -d
```

```bash
docker exec -it sqlalchemy-fake-model bash
```

### Run tests
```bash
docker exec -it sqlalchemy-fake-model pytest
```

### Run linting
```bash
docker exec -it sqlalchemy-fake-model sh -c "isort ."
docker exec -it sqlalchemy-fake-model sh -c "autoflake --in-place --remove-all-unused-imports --ignore-init-module-imports --recursive ."
docker exec -it sqlalchemy-fake-model black .
```
