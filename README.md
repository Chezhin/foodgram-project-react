# Проект Foodgram - «Продуктовый помощник»
Сервис, который позволяет пользователям публиковать свои рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Запуск проекта

Для работы с проектом в контейнерах должен быть установлен Docker и docker-compose.

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```
git clone https://github.com/Chezhin/foodgram-project-react.git
```
Перейдите в папку foodgram-project-react/infra
```
cd foodgram-project-react/infra
```

Выполните команду для сборки контейнеров:
```
docker-compose up -d --build
```

### Выполните миграции:
```
docker-compose exec backend python manage.py migrate
```

### Загрузите статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```

### Создайте суперюзера:
```
docker-compose exec backend python manage.py createsuperuser
```

Проект запущен и доступен по [адресу](http://84.201.140.189/)

### Автор: Руслан Чежин.
