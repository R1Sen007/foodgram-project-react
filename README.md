# *Проект FoodGram*

# [ССЫЛКА НА ПРОЕКТ](https://foodgram-project.sytes.net/)
## Авторы
 - [Павел Тыртин](https://github.com/R1Sen007)

## Технологии
### backend
 - Django v3.2
 - django-filter v23.5
 - djangorestframework v3.12.4
 - djoser
 - pytest v6.2.4
### frontend
 - React
### deploy/server
 - Nginx
 - gunicorn
 - docker
 - docker-compose

## Описание:

***Пользователи сервиса FoodGram могут делиться своими уникальными рецептами со всем миром! ***

## Как развернуть проект:

- Клонировать репозиторий
```
git clone https://github.com/R1Sen007/foodgram-project-react.git
```

- Перейти в корень проекта и создать файл ".env" с переменными окружения 
```
touch .env
```

- Файл должен содержать следующие переменные:
```
POSTGRES_USER=...
POSTGRES_PASSWORD=...
POSTGRES_DB=db
DB_HOST=...
DB_PORT=...
HOST_PORT=9000
CONTAINER_PORT=80
```

- Запусть контейнеры
```
docker compose up
```

- Провести миграции
```
docker compose exec backend python manage.py migrate
```

- Собрать статику
```
docker compose exec backend python manage.py collectstatic
docker compose exec backend cp -r /app/collected_static/. /backend_static/static/
```

- Импортировать ингредиенты
```
docker compose exec backend python manage.py import_ingredients
```

- Импортировать тэги
```
docker compose exec backend python manage.py import_tags
```

- Ввести в адресной строке браузера localhost