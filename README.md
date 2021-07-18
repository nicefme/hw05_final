# Yatube
## Cоциальная сеть для публикации постов


### Что это за проект

Yatube - разработан на архитектуре Model-View-Template. Реализованы комментарии к публикации и его рейтинг, добавление картинок к постам, пагинация по страницам и регистрация пользователей.
Стек технологий: Python 3 // Django 2.2 // SQLite


### Запуск приложения

Для запуска приложения на локальной машине необходимо:

- Клонировать репозиторий: ``` git clone ... ```;
- Файл ``` empty.env ``` переименовать в ``` .env ``` и в файле указать значение для поля ``` POSTGRES_PASSWORD ```;
- В командной строке linux выполнить команду ``` docker-compose up -d --build ``` для развертывания проекта через docker;
- Сделать миграции:  
``` sudo docker-compose exec web python manage.py makemigrations users ```  
``` sudo docker-compose exec web python manage.py makemigrations reviews ```  
``` sudo docker-compose exec web python manage.py makemigrations titles ```  
``` docker-compose exec web python manage.py migrate --noinput ```
- Собрать статику:  
``` docker-compose exec web python manage.py collectstatic --no-input ```

Готово! Сайт доступен по адресу http://127.0.0.1/


### Создание суперпользователя

Для создания суперпользователя необходимо ввести команду:  
``` python manage.py createsuperuser ```  
и далее следовать инструкциям на экране.


### Заполнение базы данных

Для того, чтобы заполнить БД необходимо перейти по ссылке http://127.0.0.1/admin и залогиниться под суперпользователем.