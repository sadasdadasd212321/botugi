import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

TOKEN = '6239412265:AAF4TPuqoAAbEZe9jjzx3WM0_0yBQqWjt-s'
OPERATOR_CHAT_ID = '1467358924'
active_chats = {}


bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.chat.id
    active_chats[user_id] = "start"  # Добавляем ID пользователя в словарь с состоянием "start"
    
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_complaint = telebot.types.KeyboardButton(text="Звернення громадян на неправомірні дії поліцейських")
    button_anonymous = telebot.types.KeyboardButton(text="Анонімне звернення громадян на неправомірні дії поліцейських")
    button_proposal = telebot.types.KeyboardButton(text="Пропозиції (зауваження) громадян щодо підвищення результативності надання поліцейських послуг")
    button_gratitude = telebot.types.KeyboardButton(text="Інформація про позитивні тенденції в роботі органу (підрозділу) поліції")
    button_policecomplaint = telebot.types.KeyboardButton(text="Звернення поліцейських з питань роботи дій керівництва та стану забезпечення службової діяльності")
    button_anonpolicecomplaint = telebot.types.KeyboardButton(text="Анонімне звернення поліцейських з питань роботи дій керівництва та стану забезпечення службової діяльності")
    button_contacts = telebot.types.KeyboardButton(text="Контакти \U0001F4F1")
    keyboard.add(button_complaint, button_anonymous, button_proposal, button_gratitude, button_policecomplaint, button_anonpolicecomplaint, button_contacts)
    bot.send_message(message.chat.id, "Вітаю! Виберіть потрібну опцію:", reply_markup=keyboard)

def send_message_with_retry(chat_id, message):
    while True:
        try:
            bot.send_message(chat_id, message)
            break
        except Exception:
            print("Error occurred. Retrying...")
            

@bot.message_handler(func=lambda message: message.text == "Контакти \U0001F4F1")
def send_contacts(message):
    contact_info = "Ви можете звернутися за такими контактними даними:\n\n" \
                   "Email: ugi.zak.police@gmail.com \U0001F4E7\n" \
                   "Телефон: 380XXXXXXXXX \U0001F4F1\n" \
                   "Адреса: м. Ужгород, вул. Центральна 5. \U0001F3E0"
                   
    bot.send_message(message.chat.id, contact_info)
    
    
@bot.message_handler(func=lambda message: message.text == "Звернення громадян на неправомірні дії поліцейських")
def handle_complaint(message):
    complaint_type = message.text
    bot.send_message(message.chat.id, "Будь ласка, введіть свій номер телефону:")
    bot.register_next_step_handler(message, get_phone_number_complaint, {'complaint_type': complaint_type})

def get_phone_number_complaint(message, data):
    phone_number_complaint = message.text
    complaint_type = data['complaint_type']
    
    try:
        if not re.match(r'^380\d{9}$', phone_number_complaint):
            bot.send_message(message.chat.id, "Некоректний номер телефону. Введіть номер у форматі 380XXXXXXXXX:")
            bot.register_next_step_handler(message, get_phone_number_complaint, data)
            return
        
        bot.send_message(message.chat.id, "Будь ласка, опишіть подію, яка відбулась:")
        bot.register_next_step_handler(message, get_event_description_complaint, phone_number_complaint, complaint_type)
    except Exception as e:
        bot.send_message(message.chat.id, "Сталася помилка. Будь ласка, спробуйте знову пізніше.")
        print(f"Error: {e}")
        
        
def get_event_description_complaint(message, phone_number_complaint, complaint_type):
    complaint_event_description = message.text
    user_chat_id = message.chat.id
    bot.send_message(message.chat.id, "Будь ласка, надайте контактні дані:")
    bot.register_next_step_handler(message, get_contact_details, phone_number_complaint, complaint_event_description, complaint_type, user_chat_id)

def get_contact_details(message, phone_number_complaint, complaint_event_description, complaint_type, user_chat_id):
    contact_details = message.text
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = None
        
    # Format the complaint data
    data = {
        "Тип звернення": complaint_type,
        "Номер телефону": phone_number_complaint,
        "Подія": complaint_event_description,
        "Контактні дані користувача": contact_details,
        "Нікнейм користувача": username,
        "Чат ID користувача": user_chat_id
    }
    formatted_data = format_complaint_data(data, complaint_event_description, username, user_chat_id)

    # Send the complaint message
    bot.send_message(OPERATOR_CHAT_ID, formatted_data)

def format_complaint_data(data, event_description, username, user_chat_id):
    complaint_type = data["Тип звернення"]
    phone_number_complaint = data["Номер телефону"]
    contact_details = data["Контактні дані користувача"]

    message = f"Тип звернення: {complaint_type}\n"
    message += f"Номер телефону: {phone_number_complaint}\n"
    message += f"Подія: {event_description}\n"
    message += f"Контактні дані користувача: {contact_details}\n"
    message += f"Чат ID користувача: {user_chat_id}\n"
    if username:
        message += f"Нікнейм користувача: @{username}\n"

    return message
@bot.message_handler(func=lambda message: message.text == "Анонімне звернення громадян на неправомірні дії поліцейських")
def handle_anonymous_complaint(message):
    bot.send_message(message.chat.id, "Будь ласка, опишіть подію, яка відбулась:")
    bot.register_next_step_handler(message, get_event_description, anonymous=True)
    

def get_event_description(message, anonymous):
    event_description = message.text
    user_chat_id = message.chat.id
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = None

    # Сохранение данных в переменные
    if anonymous:
        complaint_type = "Анонімне звернення громадян на неправомірні дії поліцейських"
    else:
        complaint_type = "Звернення громадян на неправомірні дії поліцейських"

    # Отправка данных оператору
    operator_message = format_complaint_data(complaint_type, event_description, username, user_chat_id)

    # Создание инлайн-кнопки "Відповісти" для оператора
    reply_button_operator = types.InlineKeyboardMarkup()
    reply_button_operator.add(types.InlineKeyboardButton(text='Відповісти', callback_data=f'reply_{user_chat_id}'))
    
    bot.send_message(OPERATOR_CHAT_ID, operator_message, reply_markup=reply_button_operator)

    # Благодарственное сообщение пользователю
    bot.send_message(message.chat.id, "Дякуємо! Ваше звернення було надіслано.")


def format_complaint_data(complaint_type, event_description, username, user_chat_id):
    message = f"Тип звернення: {complaint_type}\n"
    message += f"Подія: {event_description}\n"
    message += f"Чат - ID: {user_chat_id}\n"
    if username:
        message += f"Нікнейм користувача: @{username}\n"

    return message
    # Сохранение данных в переменные
    complaint_type = "Звернення громадян на неправомірні дії поліцейських"
    complaint_data = {
        "Тип звернення": complaint_type,
        "Номер телефону": phone_number,
        "Подія": event_description,
        "Контактні дані користувача": contact_details,
        "Нікнейм користувача": username,
        "Чат ІD": user_chat_id
    }

    # Отправка данных оператору
    operator_message = format_complaint_data(complaint_data)
    bot.send_message(OPERATOR_CHAT_ID, operator_message)

    # Благодарственное сообщение пользователю
    bot.send_message(message.chat.id, "Дякуємо! Ваше звернення було надіслано.")

@bot.message_handler(func=lambda message: message.text == "Пропозиції (зауваження) громадян щодо підвищення результативності надання поліцейських послуг")
def handle_proposal(message):
    bot.send_message(message.chat.id, "Будь ласка, введіть свій номер телефону:")
    bot.register_next_step_handler(message, get_phone_number)

def get_phone_number(message):
    user_chat_id = message.chat.id
    phone_number = message.text

    if not re.match(r'^380\d{9}$', phone_number):
        bot.send_message(message.chat.id, "Некоректний номер телефону. Введіть номер у форматі 380XXXXXXXXX:")
        bot.register_next_step_handler(message, get_phone_number)
        return 
        
        
    bot.send_message(message.chat.id, "Будь ласка, введіть вашу пропозицію чи зауваження:")
    bot.register_next_step_handler(message, get_proposal, phone_number, user_chat_id)


def get_proposal(message, phone_number, user_chat_id):
    proposal = message.text
    bot.send_message(message.chat.id, "Будь ласка, введіть ваше ПІБ:")
    bot.register_next_step_handler(message, get_contact_info, phone_number, user_chat_id, proposal)

def get_contact_info(message, phone_number, user_chat_id, proposal):
    contact_info = message.text
    if message.from_user.username:
        username = message.from_user.username
    else:
        username = None

    # Сохранение данных в переменные
    complaint_type = "Пропозиції (зауваження) громадян щодо підвищення результативності надання поліцейських послуг"

    # Отправка данных оператору
    operator_message = format_proposal_data(complaint_type, phone_number, proposal, contact_info, username, user_chat_id)
    bot.send_message(OPERATOR_CHAT_ID, operator_message)

    # Благодарственное сообщение пользователю
    bot.send_message(message.chat.id, "Дякуємо! Ваша пропозиція була надіслана.")

def format_proposal_data(complaint_type, phone_number, proposal, contact_info, username, user_chat_id):
    message = f"Тип звернення: {complaint_type}\n"
    message += f"Номер телефону: {phone_number}\n"
    message += f"Пропозиція: {proposal}\n"
    message += f"Контактні дані користувача: {contact_info}\n"
    message += f"Chat ID користувача: {user_chat_id}\n"
    if username:
        message += f"Нікнейм користувача: @{username}\n"
    return message    


@bot.message_handler(func=lambda message: message.text == "Інформація про позитивні тенденції в роботі органу (підрозділу) поліції")
def gratitude(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Будь ласка, введіть ваш номер телефону:")
    bot.register_next_step_handler(message, get_phone_number_gratitude)


def get_phone_number_gratitude(message):
    phone_number = message.text
    user_chat_id = message.chat.id

    if not re.match(r'^380\d{9}$', phone_number):
        bot.send_message(message.chat.id, "Некоректний номер телефону. Введіть номер у форматі 380XXXXXXXXX:")
        bot.register_next_step_handler(message, get_phone_number_gratitude)
        return

    bot.send_message(message.chat.id, "Будь ласка, опишіть подію, за яку ви бажаєте подякувати:")
    bot.register_next_step_handler(message, get_event_description_gratitude, phone_number, user_chat_id)


def get_event_description_gratitude(message, phone_number, user_chat_id):
    event_description = message.text

    bot.send_message(message.chat.id, "Будь ласка, введіть дані поліцейського або підрозділу, за який ви хочете висловити подяку.\nЯкщо такого немає, напишіть Ні в чат.")
    bot.register_next_step_handler(message, get_officer_info_gratitude, phone_number, event_description, user_chat_id)


def get_officer_info_gratitude(message, phone_number, event_description, user_chat_id):
    officer_info = message.text

    if officer_info.lower() == "Ні":
        officer_info = ""

    bot.send_message(message.chat.id, "Будь ласка, введіть ваші контактні дані (ПІБ, електронна пошта):")
    bot.register_next_step_handler(message, get_contact_info_gratitude, phone_number, event_description, officer_info, user_chat_id)


def get_contact_info_gratitude(message, phone_number, event_description, officer_info, user_chat_id):
    contact_info = message.text

    bot.send_message(OPERATOR_CHAT_ID, f"Тип звернення: Подяка\n"
                                       f"Номер телефону: {phone_number}\n"
                                       f"Подія: {event_description}\n"
                                       f"Інформація про поліцейського: {officer_info}\n"
                                       f"Контактні дані користувача: {contact_info}\n"
                                       f"Chat ID користувача: {user_chat_id}\n"
                                       f"Нік нейм користувача: @{message.from_user.username}")

    bot.send_message(message.chat.id, "Дякуємо за вашу подяку!")
    
    
@bot.message_handler(func=lambda message: message.text == "Звернення поліцейських з питань роботи дій керівництва та стану забезпечення службової діяльності")
def police_appeal(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Будь ласка, введіть ваш номер телефону:")
    bot.register_next_step_handler(message, get_phone_number_appeal, chat_id)


def get_phone_number_appeal(message, chat_id):
    phone_number = message.text

    if not re.match(r'^380\d{9}$', phone_number):
        bot.send_message(message.chat.id, "Некоректний номер телефону. Введіть номер у форматі 380XXXXXXXXX:")
        bot.register_next_step_handler(message, get_phone_number_appeal, chat_id)
        return

    bot.send_message(message.chat.id, "Будь ласка, опишіть подію, з приводу якої ви звертаєтесь до поліції:")
    bot.register_next_step_handler(message, get_event_description_appeal, chat_id, phone_number)


def get_event_description_appeal(message, chat_id, phone_number):
    event_description = message.text

    bot.send_message(message.chat.id, "Будь ласка, введіть ваші контактні дані (ПІБ, електронна пошта):")
    bot.register_next_step_handler(message, get_contact_info_appeal, chat_id, phone_number, event_description)


def get_contact_info_appeal(message, chat_id, phone_number, event_description):
    contact_info = message.text

    reply_button_operator = types.InlineKeyboardMarkup()
    reply_button_operator.add(types.InlineKeyboardButton(text='Відповісти', callback_data=f'activate_chat_{chat_id}'))

    bot.send_message(OPERATOR_CHAT_ID, 
                     f"Тип звернення: Звернення поліцейського\n"
                     f"Номер телефону: {phone_number}\n"
                     f"Подія: {event_description}\n"
                     f"Контактні дані користувача: {contact_info}\n"
                     f"Chat ID користувача: {chat_id}\n"
                     f"Нік нейм користувача: @{message.from_user.username}",
                     reply_markup=reply_button_operator)


    bot.send_message(message.chat.id, "Дякуємо за ваше звернення! Бот благодарит пользователя!")
    
@bot.message_handler(func=lambda message: message.text == "Анонімне звернення поліцейських з питань роботи дій керівництва та стану забезпечення службової діяльності")
def anonymous_police_appeal(message):
    chat_id = message.chat.id

    bot.send_message(chat_id, "Будь ласка, опишіть подію, з приводу якої ви звертаєтесь до поліції:")
    bot.register_next_step_handler(message, get_event_description_anonymous_appeal, chat_id)


def get_event_description_anonymous_appeal(message, chat_id):
    event_description = message.text

    bot.send_message(OPERATOR_CHAT_ID, f"Тип звернення: Анонімне Звернення поліцейського\n"
                                       f"Подія: {event_description}\n"
                                       f"Chat ID користувача: {chat_id}\n"
                                       f"Нік нейм користувача: @{message.from_user.username}")

    bot.send_message(message.chat.id, "Дякуємо за ваше анонімне звернення! Бот благодарит пользователя!")
 
# Переменная для хранения активного чата
active_chat_id = None

# Функция для обработки команды /reply
@bot.message_handler(commands=['reply'])
def activate_chat(message):
    global active_chat_id
    active_chat_id = message.text.split()[1]
    bot.send_message(active_chat_id, 'Менеджер вошел в чат. Для ответа оператору нажмите кнопку "Ответить" и введите ваш текст.')



# Обработчик инлайн-кнопки "Ответить" для клиента
@bot.callback_query_handler(func=lambda call: call.data == 'reply_to_client')
def reply_to_operator_from_client(call):
    # Запрашиваем у пользователя текст ответа
    bot.send_message(call.message.chat.id, 'Введіть відповідь на повідомлення:')

# Обработчик ответа пользователя
@bot.message_handler(func=lambda message: active_chat_id == str(message.chat.id))
def reply_from_client(message):
    print("Received a message from the client")  # Добавьте эту строку
    bot.send_message(OPERATOR_CHAT_ID, message.text)
    # Создание инлайн-кнопки "Ответить" для оператора
    reply_button_operator = types.InlineKeyboardMarkup()
    reply_button_operator.add(types.InlineKeyboardButton(text='Відповісти', callback_data=f'activate_chat_for_operator_{message.chat.id}'))
    bot.send_message(OPERATOR_CHAT_ID, 'Новое сообщение от клиента. Нажмите кнопку ниже, чтобы ответить.', reply_markup=reply_button_operator)

@bot.message_handler(func=lambda message: active_chat_id is not None and str(message.chat.id) != active_chat_id)
def send_message_to_client(message):
    if active_chat_id is not None:
        # Создание инлайн-кнопки "Ответить"
        reply_button = types.InlineKeyboardMarkup()
        reply_button.add(types.InlineKeyboardButton(text='Відповісти', callback_data='reply_to_client'))

        # Отправка сообщения пользователю с инлайн-кнопкой "Ответить" и инструкцией
        instruction = 'Для відповіді черговому натисніть кнопку "Відповісти" та відправте текст відповіді.'
        bot.send_message(active_chat_id, f'{message.text}\n\n{instruction}', reply_markup=reply_button)
    else:
        # Если активный чат не установлен, отправляем сообщение об ошибке
        bot.reply_to(message, 'Активный чат не установлен.')
# Обработчик инлайн-кнопки "Ответить" для оператора

@bot.callback_query_handler(func=lambda call: call.data.startswith('activate_chat_for_operator'))
def activate_chat_for_operator(call):
    global active_chat_id
    active_chat_id = call.data.split('_')[-1]  # Извлечь chat_id клиента из callback_data
    bot.send_message(call.from_user.id, 'Менеджер вошел в чат. Для ответа клиенту напишите ваш текст.')  # Отправить сообщение оператору


while True:
    try:
        bot.polling()
    except Exception:
        print("Error occurred. Restarting bot...")
