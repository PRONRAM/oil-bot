from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🏢 О компании'),
        KeyboardButton('💪 Личность и адаптация'),
        KeyboardButton('📚 Обучение маслам'),
        KeyboardButton('ℹ️ Помощь')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню ветки 1 (О компании)
def company_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        KeyboardButton('📜 История компании'),
        KeyboardButton('⭐ Миссия и ценности'),
        KeyboardButton('📋 Наши стандарты работы'),
        KeyboardButton('📞 Структура и контакты'),
        KeyboardButton('🏠 В главное меню')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню ветки 2 (Адаптация)
def adaptation_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🔥 Профессиональное выгорание'),
        KeyboardButton('👥 Я и коллектив сейчас'),
        KeyboardButton('😤 Сложные клиенты'),
        KeyboardButton('📈 Моя личность + карьера'),
        KeyboardButton('⚡ Энергия смены'),
        KeyboardButton('📊 Тест на адаптацию'),
        KeyboardButton('🏠 В главное меню')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню для сложных клиентов
def difficult_clients_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🤬 Хам'),
        KeyboardButton('😢 Жертва'),
        KeyboardButton('🎭 Манипулятор'),
        KeyboardButton('🔄 Ещё тип клиента'),
        KeyboardButton('◀️ В меню адаптации')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню для карьеры и личности
def career_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        KeyboardButton('✅ Чек-лист роста'),
        KeyboardButton('💪 Как прокачать уверенность?'),
        KeyboardButton('◀️ В меню адаптации')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню энергии смены
def energy_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        KeyboardButton('⏱️ 30 секунд между клиентами'),
        KeyboardButton('⚓ Якорь спокойствия'),
        KeyboardButton('🎯 Ритуал после смены'),
        KeyboardButton('◀️ В меню адаптации')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню выгорания
def burnout_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        KeyboardButton('💡 Что делать?'),
        KeyboardButton('😫 А если уже всё бесит?'),
        KeyboardButton('◀️ В меню адаптации')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню коллектива
def team_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        KeyboardButton('⚠️ Что делать с токсичным коллегой?'),
        KeyboardButton('📈 Как повысить свой авторитет?'),
        KeyboardButton('◀️ В меню адаптации')
    ]
    keyboard.add(*buttons)
    return keyboard

# Меню обучения маслам
def oil_learning_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('📖 Начать обучение'),
        KeyboardButton('📊 Мой прогресс'),
        KeyboardButton('🔄 Пропущенный урок'),
        KeyboardButton('📝 Итоговый экзамен'),
        KeyboardButton('🏠 В главное меню')
    ]
    keyboard.add(*buttons)
    return keyboard

# Inline клавиатура для тестов
def yes_no_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    buttons = [
        InlineKeyboardButton(text='✅ Да', callback_data='answer_yes'),
        InlineKeyboardButton(text='❌ Нет', callback_data='answer_no')
    ]
    keyboard.add(*buttons)
    return keyboard

def test_options_keyboard(options: list):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, option in enumerate(options, 1):
        keyboard.add(InlineKeyboardButton(text=option, callback_data=f'test_answer_{i}'))
    return keyboard

def continue_test_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(InlineKeyboardButton(text='📝 Продолжить тест', callback_data='continue_test'))
    return keyboard
