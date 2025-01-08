from gc import callbacks

from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackQueryHandler, CommandHandler

from gpt import *
from util import *

async def start(update, context): # Самая начальная функция описывает весь возможный функционал
    dialog.mode = "main"
    text = load_message("main")
    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await   show_main_menu(update, context, commands={
        "start":"Запустить",
        "profile":"генерация Tinder-профля 😎",
        "opener":"сообщение для знакомства 🥰",
        "message":"переписка от вашего имени 😈",
        "date":"переписка со звездами 🔥",
        "gpt":"Общение с ИИ 🧠"
    })

async def gpt_dialog(update, context): # Режим общения с чатом GPT дает короткий ответ на вопрос
    my_message = await send_text(update, context, "Чат GPT 🧠 набирает сообщение...")
    text = update.message.text
    prompt = load_prompt("gpt")
    answer = await chatgpt.send_question(prompt,text)
    await my_message.edit_text(answer)

async def hello(update, context): # функция режима общения, в зависимости от которого выбирается сценарий
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "*Привет*")
        await send_text(update, context, "_Как дела?_")
        await send_text(update, context, "Вы написали "+ update.message.text)
        await send_photo(update, context, "avatar_main")
        await send_text_buttons(update, context,"Запустить процесс?", {
            "start":"Запустить",
            "stop":"Остановить"
        })

async def hello_button(update, context): #Кнопка запуска
    query= update.callback_query.data
    if query == "start":
        await send_text(update,context,"Процесс запущен")
        await send_photo(update, context, "zapusk")
    else:
        await send_text(update, context, "Процесс остановлен")
        await send_photo(update, context, "stop")

async def gpt(update, context): # Функция GPT
    dialog.mode = "gpt"     #сценарий общения
    text = load_message("gpt") # принимает сообщение от пользователя для чата
    await send_photo(update, context, "gpt") # Отправляет фото чата
    await send_text(update, context, text) # Выдает ответ на вопрос

async def date(update, context):
    dialog.mode = "date"
    text = load_message("date")
    await send_photo(update, context, "date")
    await send_text_buttons(update, context, text,{ # Кнопки с выбором звезд
        "date_grande":"Ариана Гранде 🔥",
        "date_robbie": "Марго Робби 🔥🔥",
        "date_zendaya": "Зендея     🔥🔥🔥",
        "date_gosling": "Райан Гослинг 😎",
        "date_hardy": "Том Харди   😎😎",
    } )

async def date_button(update, context):
    query= update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(update,context, "Отличный выбор! Пригласите собеседника на свидание за 5 сообщений")

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt) # Отправляет чату выбранную модель поведения

async def date_dialog(update, context): # Функция общения со звездой
    text = update.message.text
    my_message = await send_text(update, context, "Собеседник набирает сообщение...")
    answer = await chatgpt.add_message(text)
    await my_message.edit_text(answer)

async def message(update, context): 
    dialog.mode = "message"
    text = load_message("message")
    await send_photo(update, context, "message")
    await send_text_buttons(update, context, text, {
        "message_next": "Следущее сообщение",
        "message_date": "Пригласить на свидание"
    })
    dialog.list.clear()

async def message_button(update, context):
    query = update.callback_query.data
    await update.callback_query.answer()

    prompt = load_prompt(query)
    user_chat_history = '\n\n'.join(dialog.list)
    my_message = await send_text(update, context, "Чат GPT 🧠 думает...")
    answer = await  chatgpt.send_question(prompt, user_chat_history)
    await my_message.edit_text(answer)

async def message_dialog(update, context):
    text = update.message.text
    dialog.list.append(text)

async def profile(update, context):
    dialog.mode = "profile"
    text = load_message("profile")
    await send_photo(update, context, "profile")
    await send_text(update, context, text)
    dialog.user.clear() # очистка истории общения перед вопросами
    dialog.count = 0    # Счетчик вопросов, чтобы определить очередность и режим диалога
    await send_text(update, context, "Сколько вам лет?")

async def profile_dialog(update, context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Кем вы работаете?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "У вас есть хобби?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Что вам НЕ нравится в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("profile") # эти действия стоят в крайнем elif потому что иначе начинаются раньше, чем закончатся вопросы
        user_info = dialog_user_info_to_str(dialog.user)
        my_message = await send_text(update, context, "Чат GPT 🧠 генерирует профиль...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener(update,context): # по аналогии с предыдущими двумя функциями
    dialog.mode = "opener"
    text = load_message("opener")
    await send_photo(update, context, "opener")
    await send_text(update, context, text)

    dialog.user.clear()
    dialog.count = 0
    await send_text(update, context, "Имя девушки?")

async def opener_dialog(update,context):
    text = update.message.text
    dialog.count += 1

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько ей лет?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцените ее внешность 1-10 баллов?")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Кем она работает?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Цель знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text
        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)
        my_message = await send_text(update, context, "Чат GPT 🧠 генерирует сообщение...")
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


dialog = Dialog()
dialog.mode = None    #Режим общения, в зависимости от нажатой кнопки
dialog.list = []     # История общения
dialog.count = 0     # Счетчик вопросов
dialog.user = {}    

chatgpt = ChatGptService(token="Здесь стоит токен чата GPT  я использовал версию 3.5 турбо")
app = ApplicationBuilder().token("Api token").build()

app.add_handler(CommandHandler("start", start)) # вбиваем наши команды
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("date", date))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))

app.add_handler(MessageHandler(filters.TEXT &~ filters.COMMAND, hello)) # установили фильр на команды, чтобы не врезалось в start

app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))  #Выборка для нащих кнопок
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))
app.add_handler(CallbackQueryHandler(hello_button))
app.run_polling()
