import os
import requests
import json
import time
import logging

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    logger.error("❌ ОШИБКА: BOT_TOKEN не найден в переменных окружения!")
    exit(1)

logger.info(f"✅ Бот запускается с токеном: {BOT_TOKEN[:10]}...")

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0

def send_message(chat_id, text):
    """Отправка сообщения"""
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        if response.status_code == 200:
            logger.info(f"✅ Сообщение отправлено в чат {chat_id}")
        else:
            logger.error(f"❌ Ошибка отправки: {response.status_code}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")

def handle_start(chat_id):
    """Обработка команды /start"""
    text = """👋 <b>Добро пожаловать!</b>

Я бот компании <b>«Белоруснефть-Гомельоблнефтепродукт»</b>

🤖 Доступные команды:
/start - начать работу
/company - информация о компании
/help - помощь

Просто напишите любое сообщение, и я отвечу!"""
    send_message(chat_id, text)

def handle_company(chat_id):
    """Информация о компании"""
    text = """🏭 <b>О компании</b>

<b>«Белоруснефть-Гомельоблнефтепродукт»</b>

📅 <b>История:</b>
• Основана в 1968 году
• В составе «Белоруснефть» с 2005 года

📋 <b>Основные виды деятельности:</b>
• Оптовая и розничная торговля нефтепродуктами
• Розничная торговля, общественное питание
• Оптовая торговля сопутствующими товарами

⭐ <b>Наши ценности:</b>
• Клиентоцентричность
• Честность
• Ответственность
• Профессионализм
• Командность

<i>Вы — часть большой истории. Спасибо, что с нами!</i>"""
    send_message(chat_id, text)

def handle_help(chat_id):
    """Помощь"""
    text = """❓ <b>Помощь</b>

Доступные команды:
/start - начать работу
/company - информация о компании
/help - показать эту справку

Скоро будут добавлены:
• Тест на адаптацию
• Обучение по маслам
• Советы по работе с клиентами

Следите за обновлениями!"""
    send_message(chat_id, text)

def handle_unknown(chat_id, text):
    """Неизвестная команда"""
    response = f"""🤔 Я не понимаю команду: <b>{text}</b>

Доступные команды:
/start - начать работу
/company - информация о компании
/help - помощь

Просто нажмите на нужную команду в меню!"""
    send_message(chat_id, response)

def process_message(message):
    """Обработка входящих сообщений"""
    try:
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        logger.info(f"📨 Получено сообщение от {chat_id}: {text}")
        
        # Обработка команд
        if text == '/start':
            handle_start(chat_id)
        elif text == '/company':
            handle_company(chat_id)
        elif text == '/help':
            handle_help(chat_id)
        else:
            handle_unknown(chat_id, text)
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")

def main():
    """Главный цикл бота"""
    global last_update_id
    
    logger.info("🚀 Бот запущен и начал прослушивание сообщений...")
    
    while True:
        try:
            # Получаем обновления
            url = f"{BASE_URL}/getUpdates"
            params = {
                "offset": last_update_id + 1,
                "timeout": 30
            }
            
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get('ok'):
                updates = data.get('result', [])
                for update in updates:
                    last_update_id = update['update_id']
                    
                    if 'message' in update:
                        process_message(update['message'])
            else:
                logger.error(f"❌ Ошибка API: {data}")
                
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Таймаут, продолжаем...")
        except Exception as e:
            logger.error(f"❌ Критическая ошибка: {e}")
            time.sleep(5)

if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("🤖 ЗАПУСК БОТА")
    logger.info("=" * 50)
    main()
