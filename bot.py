import logging
import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Токен из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    print("ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    exit(1)

# Настройка бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# Клавиатуры
def main_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    buttons = [
        KeyboardButton('🏢 О компании'),
        KeyboardButton('💪 Личность и адаптация'),
        KeyboardButton('📚 Обучение маслам')
    ]
    keyboard.add(*buttons)
    return keyboard

def company_menu():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = [
        KeyboardButton('📜 История компании'),
        KeyboardButton('⭐ Миссия и ценности'),
        KeyboardButton('📋 Наши стандарты работы'),
        KeyboardButton('📞 Контакты'),
        KeyboardButton('🏠 Главное меню')
    ]
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Добро пожаловать в бот компании «Белоруснефть-Гомельоблнефтепродукт».\n\n"
        "Выберите раздел в меню:",
        reply_markup=main_menu()
    )

@dp.message_handler(lambda message: message.text == '🏠 Главное меню')
async def back_to_main(message: types.Message):
    await message.answer("Главное меню:", reply_markup=main_menu())

@dp.message_handler(lambda message: message.text == '🏢 О компании')
async def about_company(message: types.Message):
    await message.answer(
        "🏭 «Белоруснефть-Гомельоблнефтепродукт»\n\n"
        "Компания создана в 1968 году.\n"
        "В составе компании «Белоруснефть» с 2005 года.\n\n"
        "Основные виды деятельности:\n"
        "• Оптовая и розничная торговля нефтепродуктами\n"
        "• Розничная торговля, общественное питание\n"
        "• Оптовая торговля сопутствующими товарами\n\n"
        "Вы — часть большой истории. Спасибо, что с нами!",
        reply_markup=company_menu()
    )

@dp.message_handler(lambda message: message.text == '📜 История компании')
async def history(message: types.Message):
    await message.answer(
        "📜 История компании:\n\n"
        "«Белоруснефть-Гомельоблнефтепродукт» — часть системы «Белоруснефть».\n\n"
        "📅 1968 год — создание предприятия\n"
        "📅 2005 год — вхождение в состав «Белоруснефть»\n\n"
        "Сегодня компания — лидер на рынке нефтепродуктов Гомельской области.",
        reply_markup=company_menu()
    )

@dp.message_handler(lambda message: message.text == '⭐ Миссия и ценности')
async def mission(message: types.Message):
    await message.answer(
        "⭐ Наша миссия:\n\n"
        "«Постоянно совершенствуясь, расширяя сферу услуг, сохраняя лидерство на рынке, Мы движемся, опережая время.»\n\n"
        "💎 Ценности:\n"
        "• Клиентоцентричность\n"
        "• Честность\n"
        "• Ответственность\n"
        "• Профессионализм\n"
        "• Командность\n\n"
        "Вы — главный носитель этих ценностей на своей АЗС!",
        reply_markup=company_menu()
    )

@dp.message_handler(lambda message: message.text == '📋 Наши стандарты работы')
async def standards(message: types.Message):
    await message.answer(
        "📋 Стандарты работы:\n\n"
        "1️⃣ Чистота и порядок\n"
        "2️⃣ Единое приветствие: «Добрый день! Чем могу помочь?»\n"
        "3️⃣ Компетентность: «Я уточню у старшего оператора»\n"
        "4️⃣ Прощание: «Спасибо за визит! Хорошей дороги!»",
        reply_markup=company_menu()
    )

@dp.message_handler(lambda message: message.text == '📞 Контакты')
async def contacts(message: types.Message):
    await message.answer(
        "📞 Контакты:\n\n"
        "📍 Адрес: пос. Янтарный 12, Гомельский р-н\n\n"
        "📱 Телефоны:\n"
        "+375 (232) 23-75-75\n"
        "+375 (232) 24-22-40\n\n"
        "🔸 Диспетчерская: +375(232) 24-22-88\n"
        "🔸 Отдел кадров: номер у старшего оператора\n"
        "🔸 Горячая линия: +375 (29) 6-431-431",
        reply_markup=company_menu()
    )

@dp.message_handler(lambda message: message.text == '💪 Личность и адаптация')
async def adaptation(message: types.Message):
    await message.answer(
        "💪 Поддержка сотрудников\n\n"
        "Здесь вы найдете:\n"
        "• Признаки профессионального выгорания\n"
        "• Техники восстановления энергии\n"
        "• Как работать со сложными клиентами\n"
        "• Чек-листы для карьерного роста\n"
        "• Советы по отношениям в коллективе\n\n"
        "Скоро все материалы будут доступны!",
        reply_markup=main_menu()
    )

@dp.message_handler(lambda message: message.text == '📚 Обучение маслам')
async def oil_learning(message: types.Message):
    await message.answer(
        "📚 Курс по моторным маслам\n\n"
        "Программа обучения (3 месяца):\n"
        "• Вязкость и сезонность\n"
        "• API, ACEA, допуски производителей\n"
        "• Типы масел (минеральные, полусинтетика, синтетика)\n"
        "• Частые ошибки операторов\n"
        "• Специализированные масла\n"
        "• Итоговый экзамен и сертификат\n\n"
        "Скоро курс будет запущен!",
        reply_markup=main_menu()
    )

if __name__ == '__main__':
    print("🤖 Бот запущен и готов к работе!")
    executor.start_polling(dp, skip_updates=True)
