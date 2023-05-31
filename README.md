# Проект Foodgram - «Продуктовый помощник»
Сервис, который позволяет пользователям публиковать свои рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Запуск проекта

Для работы с проектом в контейнерах должен быть установлен Docker и docker-compose.

Клонируйте репозиторий с проектом на свой компьютер.
В терминале из рабочей директории выполните команду:
```
git clone https://github.com/Chezhin/foodgram-project-react.git
```
Создайте и активируйте виртуальное окружение:
```bash
python -m venv venv
Windows: source venv/Scripts/activate
```
Установите зависимости из файла requirements.txt:
```bash
python3 -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
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
```bash
docker-compose exec backend python manage.py makemigrations
```
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

Проект доступен по адресу [http://localhost/](http://localhost/)

### Заполнение базы данных:

Необходимо добавить в базу данных теги и ингредиенты.
Для этого войдите в [админ-зону](http://localhost/admin/)
проекта под логином и паролем администратора.

Ингредиенты можно добавлять вручную поштучно или воспользоваться
кнопкой для импорта файла.

### Стек технологий:
- Python 3
- Django
- Django Rest
- PostgreSQL
- React
- Docker
- nginx
- gunicorn

### Автор: Руслан Чежин.
