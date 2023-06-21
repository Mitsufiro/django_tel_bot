# Django Telegram API


## Клонируем репозиторий:

    git clone https://github.com/Mitsufiro/django_telegram_bot.git
## Устанавливаем зависимости

pip install -r requirements.txt

## Migrations

При изменении модели данных необходимо создать миграцию

`python manage.py makemigrations`

Для применения изменений, необходимо запустить

`python manage.py migrate`

Создайте суперюзера
`python manage.py createsuperuser`

Добавляем свой токен для бота и запускаем файл `main.py`

* /start

 <img src="screens/start.png" width="400" height="200">

* /newtask
 <img src="screens/newtask.png" width="400" height="200">

* /tasks
 <img src="screens/tasks.png" width="400" height="150">

* /done
 <img src="screens/done.png" width="400" height="200">

* /deltask
 <img src="screens/deltask.png" width="400" height="100">

* Обработка ошибок
 <img src="screens/exceptions.png" width="400" height="200">
 <img src="screens/already_registered.png" width="400" height="50">
