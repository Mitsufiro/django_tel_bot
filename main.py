import requests
from telegram import Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    ConversationHandler,
    Filters,
    MessageHandler,
    Updater,
)

tokens = {}


def send_request(method, url, data=None):
    headers = {"Content-type": "application/json"}
    response = requests.request(method, url, headers=headers, json=data)
    return response.json()


updater = Updater(
    token="YOUR_TOKEN", use_context=True
)
dispatcher = updater.dispatcher


def start(update, context: CallbackContext):
    update.message.reply_text(
        "Привет я твой менеджер задач!\n\n"
        "Для начала давай зарегистрируемся, введи команду: /register\n\n"
        "Далее необходимо аутентифицироваться, команда: /auth\n\n"
        "Чтобы создать новую задачу, введите: /newtask\n\n"
        "Чтобы посмотреть список своих задач, введи команду: /tasks\n\n"
        "Чтобы отметить какую либо задачу как выполненную, введи: /done\n\n"
        "Если передумал отмечать задачу как выполненную то введи команду: /cancel\n\n"
        "Удаление задачи: /deltask\n\n"
        "Хорошего дня!"
    )


start_handler = CommandHandler("start", start)
dispatcher.add_handler(start_handler)

AUTH_API_URL = "http://127.0.0.1:8000/api/token/"


def auth(update: Update, context: CallbackContext) -> None:
    """Обработчик команды /auth"""
    user_id = update.effective_user.id
    # Проверяем, авторизован ли пользователь
    if is_authorized(user_id):
        context.bot.send_message(chat_id=user_id, text="Вы уже авторизованы!")
        return

    # Получаем логин и пароль пользователя из сообщения
    # Отправляем запрос на аутентификацию в Django
    response = requests.post(
        AUTH_API_URL, data={"username": user_id, "password": "s3cr3t"}
    )
    print(response.text)
    # Если аутентификация прошла успешно, сохраняем токен в базе данных
    if response.status_code == 200:
        print(response.json())
        token = response.json()["token"]
        save_token(user_id, token)
        context.bot.send_message(chat_id=user_id, text="Авторизация прошла успешно!")
    else:
        context.bot.send_message(chat_id=user_id, text="Неверный логин или пароль!")


def is_authorized(user_id: int) -> bool:
    """Проверяет, авторизован ли пользователь"""
    # В этой функции мы будем просто проверять, есть ли у пользователя токен
    return get_token(user_id) is not None


def save_token(user_id: int, token: str) -> None:
    """Сохраняет токен пользователя в базе данных"""
    tokens[user_id] = token
    print(tokens)


def get_token(user_id: int) -> str:
    """Возвращает токен пользователя из базы данных"""
    return tokens.get(user_id)


def tasks(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        context.bot.send_message(chat_id=user_id, text="Вы не авторизованы!")
        return ConversationHandler.END
    headers = {"Authorization": f"Token {tokens[user_id]}"}
    url = "http://127.0.0.1:8000/api/tasks/"
    response = requests.get(url=url, headers=headers).json()
    print("твой токен", tokens[update.effective_user.id])
    tasks_list = [
        f"{num}: {task['title']}  {task['done']} \n--{task['description']}\n"
        for task, num in zip(response, range(1, len(response) + 1))
    ]

    tasks_str = "\n".join(tasks_list)
    print(tasks_list)
    if len(tasks_list) != 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text=tasks_str)
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Список задач пуст"
        )


tasks_handler = CommandHandler("tasks", tasks)
dispatcher.add_handler(CommandHandler("auth", auth))
dispatcher.add_handler(tasks_handler)


def create_task(title, description, update):
    headers = {"Authorization": f"Token {tokens[update.effective_user.id]}"}
    url = "http://localhost:8000/api/tasks/"
    data = {
        "title": title,
        "description": description,
        "done": "❌",
    }
    response = requests.post(url, json=data, headers=headers)
    return response


def new_task_handler(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        context.bot.send_message(chat_id=user_id, text="Вы не авторизованы!")
        return ConversationHandler.END
    update.message.reply_text("Введите название задачи:")

    # Установка следующего состояния диалога в `NAME`
    return "NAME"


# Функция, которая будет вызываться при получении текстового сообщения от пользователя
def task_name_handler(update, context):
    # Получение ответа от пользователя
    task_name = update.message.text
    # Сохранение названия задачи в контекст бота
    context.user_data["task_name"] = task_name

    update.message.reply_text("Введите описание задачи:")

    # Установка следующего состояния диалога в `DESCRIPTION`
    return "DESCRIPTION"


def task_description_handler(update, context):
    # Получение ответа от пользователя
    task_description = update.message.text

    # Сохранение описания задачи в контекст бота
    context.user_data["task_description"] = task_description
    title = context.user_data["task_name"]
    description = context.user_data["task_description"]

    response = create_task(title=title, description=description, update=update)

    # Проверка успешности запроса
    if response.status_code == 201:
        update.message.reply_text("Задача сохранена.")
    else:
        update.message.reply_text("Ошибка при сохранении задачи.")

    # Сброс контекста бота
    context.user_data.clear()

    # Установка следующего состояния диалога в `ConversationHandler.END`
    return ConversationHandler.END


def cancel_handler(update, context):
    update.message.reply_text("Запись задачи отменена.")

    # Установка следующего состояния диалога в `ConversationHandler.END`
    return ConversationHandler.END


# Создание объекта ConversationHandler
conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("newtask", new_task_handler)],
    states={
        "NAME": [MessageHandler(Filters.text, task_name_handler)],
        "DESCRIPTION": [MessageHandler(Filters.text, task_description_handler)],
    },
    fallbacks=[CommandHandler("cancel", cancel_handler)],
)

updater.dispatcher.add_handler(conversation_handler)


def done_task_handler(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        context.bot.send_message(chat_id=user_id, text="Вы не авторизованы!")
        return ConversationHandler.END

    update.message.reply_text("Введите номер задачи:")

    # Установка следующего состояния диалога в `DONE`
    return "DONE"


def done(update, context):
    user_id = update.effective_user.id
    task_id = update.message.text
    if task_id == "/cancel":
        context.bot.send_message(chat_id=user_id, text=f"Отменено")
        return ConversationHandler.END
    context.user_data["task_id"] = task_id
    task_num = int(context.user_data["task_id"])
    headers = {"Authorization": f"Token {tokens[user_id]}"}
    url = "http://127.0.0.1:8000/api/tasks"
    print(task_num)
    response = requests.get(url=url, headers=headers).json()
    tasks_list = {
        num: task["id"] for task, num in zip(response, range(1, len(response) + 1))
    }
    data = {"done": "✅"}
    url = f"http://127.0.0.1:8000/api/tasks/{tasks_list[task_num]}/"
    current_task = requests.patch(url=url, headers=headers, data=data)
    print(tasks_list)
    context.bot.send_message(
        chat_id=user_id, text=f"Задача под номером {task_num} отмечена как выполненная"
    )
    context.user_data.clear()

    # Установка следующего состояния диалога в `ConversationHandler.END`
    return ConversationHandler.END


def cancel_done_handler(update, context):
    update.message.reply_text("Запись задачи отменена.")
    context.user_data.clear()
    return ConversationHandler.END


done_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler("done", done_task_handler)],
    states={
        "DONE": [MessageHandler(Filters.text, done)],
    },
    fallbacks=[CommandHandler("cancel", cancel_done_handler)],
)

updater.dispatcher.add_handler(done_conversation_handler)


def register(update, context):
    url = "http://127.0.0.1:8000/register/"
    data = {
        "username": update.effective_user.id,
        "email": "user@example.com",
        "password": "s3cr3t",
    }
    response = requests.post(url=url, data=data)
    if response.status_code == 400:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="Вы уже зарегистрированны!"
        )
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text=response.json())


register_task_handler = CommandHandler("register", register)
dispatcher.add_handler(register_task_handler)


def id_handler(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        context.bot.send_message(chat_id=user_id, text="Вы не авторизованы!")
        return ConversationHandler.END
    update.message.reply_text("Введите номер задачи:")

    context.user_data["waiting_for_task_id"] = True


def deltask(update, context):
    if "waiting_for_task_id" in context.user_data:
        task_id = int(update.message.text)
        headers = {"Authorization": f"Token {tokens[update.effective_user.id]}"}
        url = "http://127.0.0.1:8000/api/tasks"
        print(task_id)
        response = requests.get(url=url, headers=headers).json()
        tasks_list = {
            num: task["id"] for task, num in zip(response, range(1, len(response) + 1))
        }
        url = f"http://127.0.0.1:8000/api/tasks/{tasks_list[task_id]}/"
        current_task = requests.delete(url=url, headers=headers)
        print(tasks_list)
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Задача под номером {task_id} удалена",
        )

        # сбрасываем флаг ожидания ID задачи
        del context.user_data["waiting_for_task_id"]


updater.dispatcher.add_handler(CommandHandler("deltask", id_handler))
updater.dispatcher.add_handler(
    MessageHandler(Filters.text & (~Filters.command), deltask)
)
updater.start_polling()
