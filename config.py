import os
from dotenv import load_dotenv

load_dotenv()

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Настройки базы данных
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///oil_bot.db')

# Администраторы (можно указать Telegram ID через запятую)
ADMINS = list(map(int, os.getenv('ADMINS', '').split(','))) if os.getenv('ADMINS') else []
