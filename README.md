
### Описание:
Сервис позволяет пользователю публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в избранное, а также скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.
На сайте доступна система регистрации и авторизации пользователей. Неавторизованным пользователям доступен просмотр рецептов на главной странице, с фильтрацией по тегам, страниц отдельных рецептов и страниц других 
пользователей.


## Технологии:
- Python 3.8
- Django 4.2
- Django REST framework 3.14
- Api
- Nginx
- Docker
- Postgres
- Gunicorn
- JWT 


## Инструкция для запуска проекта в контейнерах локально.

* Клонируем репозиторий, заходим в директорию с `docker-compose.yaml`
```
git clone https://github.com/aidazhdanova/foodgram-project-react.git
cd foodgram-project-react/infra/
```
* Разворачиваем образы и запускаем контейнеры:

```
docker-compose up -d --build
```

* Выполняем миграции, cоздаем суперпользователя, подключаем статику:

```
docker-compose exec backend python manage.py migrate

docker-compose exec backend python manage.py createsuperuser

docker-compose exec backend python manage.py collectstatic --no-input
```

* Заполняем базу исходными данными:

```
docker-compose exec backend python manage.py loaddata ingredients.json
```

* Создаем резервную копию базы:

```
docker-compose exec backend python manage.py dumpdata > fixtures.json
```
* Команда для остановки контейнеров:
```
docker-compose down -v
```

* Создаем в корневой папке файл .env с переменными окружения, необходимыми 
для работы приложения.

Шаблон наполнения .env файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY = <Django ключ проекта>
```
После этого проект будет доступен по адресу: http://localhost/ 
С документацией можно ознакомиться по адресу: http://localhost/api/docs/

### Frontend:
https://github.com/yandex-praktikum/foodgram-project-react

### Backend:
https://github.com/aidazhdanova
