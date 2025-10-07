## Варианты запуска
- `bash run.sh`
- `docker compose up --build`


## Swagger
- `http://0.0.0.0:8000/docs#/`


## Запуск unit-тестов:
- вариант `#1` (запуск тестов в докере):
    1. `docker build -f Dockerfile_tests -t mediann-dev-tests .` - создать образ
    2. `docker run --rm mediann-dev-tests` - запустить


- вариант `#2` (запуск вручную):
    1. `python3 -m venv .venv` - установить виртуальное окружение
    2. `source .venv/bin/activate` - активировать его
    3. `pip install -r requirements.txt` - установить зависимости
    4. `pytest -q` - запустить тесты


## Посмотреть сообщения, которые поступают в топик Kafka
- `docker exec -it mediann-dev-redpanda rpk topic consume applications -X brokers=redpanda:9092`


## Переменные окружения [.env](.env) 
- Для того, чтобы запустить контейнеры, все переменные уже прописаны


## Дополнительные задания
1. ✅ Использование Docker: [Dockerfile_api](Dockerfile_api) и [Dockerfile_tests](Dockerfile_tests)
2. ✅ Логирование ошибок и событий
3. ✅ unit-тесты: [tests/](/tests/)