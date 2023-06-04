* Разворачиваем образы и запускаем контейнеры:

```
docker-compose up -d --build
```

* Выполняем миграции:

```
docker-compose exec backend python manage.py migrate
```

* Создаем суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

* Подключаем статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

* Заполняем базу исходными данными:

```
docker-compose exec backend python manage.py loaddata fixtures.json
```

* Создаем резервную копию базы:

```
docker-compose exec backend python manage.py dumpdata > fixtures.json
```
* Команда для остановки контейнеров:
```
docker-compose down -v
```
Шаблон наполнения ENV-файла
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<секретный ключ проекта django>
```