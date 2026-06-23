import os
import requests
import json
import time
import logging
import random
import threading
from flask import Flask, request

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('Bell_Oilik_Bot')

if not BOT_TOKEN:
    logger.error("❌ ОШИБКА: Bell_Oilik_Bot не найден в переменных окружения!")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Импорты базы данных
from database import init_db, save_user, get_user_progress, update_progress, save_test_result, get_completed_cycles

# Импорты контента
from oil_content import OIL_QUESTIONS_FULL, CARDS_BY_CYCLE, CASES_BY_CYCLE, STORIES_BY_CYCLE
from oil_handlers import get_cards_by_cycle, get_cases_by_cycle, get_stories_by_cycle, get_questions_by_cycle, get_test_questions

# Инициализация базы данных при запуске
init_db()

# Хранилище для временных данных (сессии, тесты)
user_test_answers = {}
user_cycle = {}
user_card_index = {}
user_cases_index = {}
user_stories_index = {}
client_index = {}

# ============= ФУНКЦИИ ДЛЯ ОТСЛЕЖИВАНИЯ ПРОГРЕССА =============

def check_cycle_completion(chat_id, cycle):
    """Проверяет, все ли материалы цикла просмотрены (из БД)"""
    progress = get_user_progress(chat_id)
    cycle_data = progress.get(cycle, {})
    cards_done = cycle_data.get('cards', False)
    cases_done = cycle_data.get('cases', False)
    stories_done = cycle_data.get('stories', False)
    return cards_done and cases_done and stories_done


def mark_material_viewed(chat_id, cycle, material):
    """Отмечает, что материал просмотрен (сохраняет в БД)"""
    update_progress(chat_id, cycle, material, True)


def get_completed_cycles_count(chat_id):
    """Получить количество пройденных циклов"""
    return len(get_completed_cycles(chat_id))


# ============= ФУНКЦИИ ОТПРАВКИ =============

def send_message(chat_id, text, reply_markup=None):
    """Отправка сообщения"""
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        logger.error(f"Ошибка: {e}")


def send_keyboard(chat_id, text, buttons):
    """Отправка сообщения с клавиатурой"""
    keyboard = {"keyboard": [[{"text": btn}] for btn in buttons], "resize_keyboard": True}
    send_message(chat_id, text, keyboard)


# ============= ОБРАБОТЧИКИ ОСНОВНЫХ РАЗДЕЛОВ =============

def handle_start(chat_id):
    """Главное меню"""
    # Сохраняем пользователя в БД
    save_user(chat_id)
    
    keyboard = {
        "keyboard": [
            [{"text": "🏢 О компании"}],
            [{"text": "💪 Личность и адаптация"}],
            [{"text": "📚 Обучение маслам"}],
            [{"text": "❓ Помощь"}]
        ],
        "resize_keyboard": True
    }
    text = f"""👋 <b>Добро пожаловать!</b>

Я бот компании <b>«Белоруснефть-Гомельоблнефтепродукт»</b>

🤖 <b>Доступные разделы:</b>
🏢 О компании — история, ценности, контакты
💪 Личность и адаптация — поддержка сотрудников
📚 Обучение маслам — курс по моторным маслам

Выберите нужный раздел в меню ниже."""
    send_message(chat_id, text, keyboard)


def show_help(chat_id):
    """Показать справку"""
    help_text = """❓ <b>Помощь по работе с ботом</b>

<b>🏢 О компании</b>
• История компании
• Миссия и ценности
• Стандарты работы
• Контакты

<b>💪 Личность и адаптация</b>
• Профессиональное выгорание
• Я и коллектив сейчас
• Сложные клиенты
• Моя личность + карьера
• Энергия смены
• Тест на адаптацию

<b>📚 Обучение маслам</b>
• 6 циклов обучения
• В каждом цикле: карточки, кейсы, истории
• После изучения материалов цикла — тест из 8 вопросов
• После всех 6 циклов — итоговый тест из 20 вопросов

<b>📌 Команды:</b>
/start — главное меню
/help — эта справка

💡 При задержке ответа: бот «засыпает» на бесплатном хостинге. Подождите 15-30 секунд."""
    buttons = ["🏠 В главное меню"]
    send_keyboard(chat_id, help_text, buttons)


def handle_company(chat_id):
    """Меню компании"""
    buttons = ["📜 История компании", "⭐ Миссия и ценности", "📋 Наши стандарты работы", "📞 Структура и контакты", "🏠 В главное меню"]
    text = """🏢 <b>Корпоративный блок</b>

Добро пожаловать! Здесь вы узнаете о компании «Белоруснефть-Гомельоблнефтепродукт».

Что вас интересует?"""
    send_keyboard(chat_id, text, buttons)


def handle_adaptation(chat_id):
    """Меню адаптации"""
    buttons = ["🔥 Профессиональное выгорание", "👥 Я и коллектив сейчас", "😤 Сложные клиенты", "📈 Моя личность + карьера", "⚡ Энергия смены", "📊 Тест на адаптацию", "🏠 В главное меню"]
    text = """💪 <b>Личность и адаптация</b>

Давай поговорим о тебе. О том, что помогает работать с кайфом, а что выматывает.

Что сейчас беспокоит или мешает?"""
    send_keyboard(chat_id, text, buttons)


# ============= ВЕТКА 1: О КОМПАНИИ (контент) =============

COMPANY_HISTORY = """
📜 <b>История компании</b>

«Белоруснефть-Гомельоблнефтепродукт» — часть системы «Белоруснефть».

📅 Компания создана в <b>1968 году</b>
📅 В составе компании «Белоруснефть» с <b>2005 года</b>

<b>Основные виды деятельности:</b>
• Оптовая и розничная торговля нефтепродуктами
• Розничная торговля, общественное питание
• Оптовая торговля сопутствующими товарами

✨ <i>Вы — часть большой истории. Спасибо, что с нами!</i>
"""

MISSION = """
⭐ <b>Миссия и ценности</b>

<b>Наша миссия:</b>
«Постоянно совершенствуясь, расширяя сферу услуг, сохраняя лидерство на рынке, Мы движемся, опережая время. Заботясь о клиенте, Мы делаем жизнь комфортнее, вдохновляем на лучшее, дарим положительные эмоции!»

<b>💎 Ценности, которые нас объединяют:</b>

✅ <b>Клиентоцентричность</b> — клиент всегда в центре нашего внимания
✅ <b>Честность</b> — говорим правду о топливе, маслах, ценах
✅ <b>Ответственность</b> — каждый сотрудник отвечает за свой участок
✅ <b>Профессионализм</b> — постоянно учимся и повышаем квалификацию
✅ <b>Командность</b> — мы одна команда

🌟 <i>Вы — главный носитель этих ценностей на своей АЗС!</i>
"""

STANDARDS = """
📋 <b>Наши стандарты работы</b>

Мы работаем по единым стандартам «Белоруснефть». Для чего это нужно? Чтобы любой клиент на любой АЗС получал одинаково качественный сервис. Вот наши 4 главных стандарта:

📌 <b>СТАНДАРТ 1 — Чистота и порядок</b>
На территории АЗС всегда чисто. Витрины, касса, форма — всё должно быть безупречно.

📌 <b>СТАНДАРТ 2 — Единое приветствие</b>
Каждый клиент слышит: «Добрый день! Чем могу помочь?». Это создаёт атмосферу доброжелательности.

📌 <b>СТАНДАРТ 3 — Компетентность</b>
Если не знаете ответ на вопрос клиента — не бойтесь сказать: «Я уточню у старшего оператора». Это лучше, чем ошибиться.

📌 <b>СТАНДАРТ 4 — Прощание</b>
Завершайте диалог фразой: «Спасибо за визит! Хорошей дороги!». Клиент должен уходить с приятным впечатлением.
"""

CONTACTS = """
📞 <b>Структура и контакты</b>

📍 <b>Адрес:</b> пос. Янтарный 12, Поколюбичский с/с, Гомельский р-н, 247012

📱 <b>Основные телефоны:</b>
+375 (232) 23-75-75
+375 (232) 24-22-40

<b>🔸 Отделы:</b>
• Диспетчерская: +375(232) 24-22-88
• Управление цифровизации: +375 (232) 79-33-25
• Отдел корпоративных клиентов: +375(232) 34-55-46, 34-61-56, 34-68-91
• Отдел оптовой торговли: +375 (232) 24-22-03
• Отдел розничной торговли: +375 (232) 24-22-43, 92-49-51
• Отдел кадров: номер у старшего оператора (пн-пт 8:00-17:00)

🔥 <b>Горячая линия:</b> +375 (29) (33) (25) 6-431-431
"""


# ============= ВЕТКА 3: ОБУЧЕНИЕ МАСЛАМ =============

def handle_oil(chat_id):
    """Главное меню обучения маслам"""
    completed_count = get_completed_cycles_count(chat_id)
    
    buttons = ["🎯 Выбрать цикл", "🏠 В главное меню"]
    
    if completed_count == 6:
        buttons.insert(0, "🎓 Итоговый тест")
    
    welcome_text = """🛢 <b>Готов стать профессионалом в масляной сфере?</b>

Я подготовил тебе <b>6 циклов простого обучения</b>.

📖 Узнавай увлекательные факты
📄 Интересную информацию про масла
💰 Помощь в работе с возражениями
📃 Подведём итоги твоих знаний тестами

<b>Выбирай цикл и полетели!</b> 😉

🎯 Выберите цикл для начала обучения."""
    
    send_keyboard(chat_id, welcome_text, buttons)


def select_cycle(chat_id):
    """Показать меню выбора цикла с отображением прогресса"""
    buttons = []
    completed_cycles = get_completed_cycles(chat_id)
    
    for cycle_num in range(1, 7):
        if cycle_num in completed_cycles:
            buttons.append(f"✅ Цикл {cycle_num} (пройден)")
        else:
            buttons.append(f"{cycle_num}️⃣ Цикл {cycle_num}")
    
    buttons.append("🏠 В главное меню")
    
    completed_count = len(completed_cycles)
    
    status_text = f"🎯 <b>Выбор цикла обучения</b>\n\n"
    status_text += f"📊 Пройдено циклов: {completed_count} из 6\n\n"
    
    if completed_count == 6:
        status_text += "🏆 <b>Вы прошли все циклы!</b>\n"
        status_text += "🎓 Итоговый тест доступен в главном меню обучения.\n\n"
    
    status_text += "Выберите цикл для изучения:"
    
    send_keyboard(chat_id, status_text, buttons)


def set_user_cycle(chat_id, cycle):
    """Установить цикл пользователя и показать меню цикла"""
    user_cycle[chat_id] = cycle
    
    progress = get_user_progress(chat_id)
    cycle_data = progress.get(cycle, {})
    
    # Формируем статус
    status_parts = []
    if cycle_data.get('cards', False):
        status_parts.append("✅ Карточки изучены")
    else:
        status_parts.append("❌ Карточки не изучены")
    
    if cycle_data.get('cases', False):
        status_parts.append("✅ Кейсы изучены")
    else:
        status_parts.append("❌ Кейсы не изучены")
    
    if cycle_data.get('stories', False):
        status_parts.append("✅ Истории изучены")
    else:
        status_parts.append("❌ Истории не изучены")
    
    status_text = f"📚 <b>Цикл {cycle}</b>\n\n" + "\n".join(status_parts)
    status_text += "\n\n<b>Доступные материалы:</b>\n"
    status_text += "📇 Знаешь ли ты — карточки\n"
    status_text += "💰 Как продать — кейсы\n"
    status_text += "📖 История на сегодня — факты"
    
    # Кнопки цикла
    buttons = ["📇 Знаешь ли ты", "💰 Как продать", "📖 История на сегодня"]
    
    # Если все материалы изучены, добавляем кнопку теста
    if check_cycle_completion(chat_id, cycle):
        status_text += "\n\n🎓 Тест по циклу доступен!"
        buttons.append("📝 Пройти тест цикла")
    
    buttons.extend(["🎯 Сменить цикл", "◀️ Назад к циклу", "🏠 В главное меню"])
    
    send_keyboard(chat_id, status_text, buttons)


def show_card(chat_id):
    """Показать карточку из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    cards_list = get_cards_by_cycle(cycle)
    
    idx = user_card_index.get(chat_id, 0)
    if idx >= len(cards_list):
        idx = 0
        user_card_index[chat_id] = 0
    
    card_text = cards_list[idx]
    total = len(cards_list)
    
    if idx == total - 1:
        mark_material_viewed(chat_id, cycle, "cards")
    
    buttons = ["◀️ Предыдущая", "▶️ Следующая", "🎲 Случайная", "◀️ Назад к циклу", "🏠 В главное меню"]
    send_keyboard(chat_id, f"📇 <b>Цикл {cycle} | Карточка {idx + 1} из {total}</b>\n\n{card_text}", buttons)


def show_case(chat_id):
    """Показать кейс из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    cases_list = get_cases_by_cycle(cycle)
    
    idx = user_cases_index.get(chat_id, 0)
    if idx >= len(cases_list):
        idx = 0
        user_cases_index[chat_id] = 0
    
    case = cases_list[idx]
    total = len(cases_list)
    
    case_text = f"<b>Кейс {idx + 1} из {total}</b>\n\n📌 <b>Ситуация:</b>\n{case['text']}\n\n✅ <b>Правильный ответ:</b>\n{case['answer']}"
    
    if idx == total - 1:
        mark_material_viewed(chat_id, cycle, "cases")
    
    buttons = ["◀️ Предыдущий", "▶️ Следующий", "🎲 Случайный", "◀️ Назад к циклу", "🏠 В главное меню"]
    send_keyboard(chat_id, f"💰 <b>Как продать? Цикл {cycle}</b>\n\n{case_text}", buttons)


def show_story(chat_id):
    """Показать историю из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    stories_list = get_stories_by_cycle(cycle)
    
    idx = user_stories_index.get(chat_id, 0)
    if idx >= len(stories_list):
        idx = 0
        user_stories_index[chat_id] = 0
    
    story = stories_list[idx]
    total = len(stories_list)
    
    if idx == total - 1:
        mark_material_viewed(chat_id, cycle, "stories")
    
    buttons = ["◀️ Предыдущая история", "▶️ Следующая история", "🎲 Случайная история", "◀️ Назад к циклу", "🏠 В главное меню"]
    send_keyboard(chat_id, f"📖 <b>Цикл {cycle} | История {idx + 1} из {total}</b>\n\n{story}", buttons)


def start_oil_test(chat_id):
    """Начать тест по циклу (8 вопросов)"""
    cycle = user_cycle.get(chat_id, 1)
    
    if not check_cycle_completion(chat_id, cycle):
        progress = get_user_progress(chat_id)
        cycle_data = progress.get(cycle, {})
        missing = []
        if not cycle_data.get('cards', False):
            missing.append("📇 Знаешь ли ты (карточки)")
        if not cycle_data.get('cases', False):
            missing.append("💰 Как продать (кейсы)")
        if not cycle_data.get('stories', False):
            missing.append("📖 История на сегодня")
        
        missing_text = "\n".join(missing)
        send_keyboard(
            chat_id,
            f"🔒 <b>Тест цикла {cycle} пока недоступен!</b>\n\n"
            f"Сначала изучите все материалы:\n\n{missing_text}\n\n"
            f"После просмотра всех материалов тест откроется автоматически.",
            ["◀️ Назад к циклу", "🏠 В главное меню"]
        )
        return
    
    questions = get_test_questions(cycle, count=8)
    user_test_answers[chat_id] = {"current": 0, "correct": 0, "questions": questions, "type": "oil", "cycle": cycle}
    send_oil_question(chat_id)


def send_oil_question(chat_id):
    """Отправить вопрос теста по маслам"""
    data = user_test_answers.get(chat_id)
    if not data or data.get("type") != "oil":
        return
    
    q_num = data["current"]
    questions = data["questions"]
    
    if q_num >= len(questions):
        finish_oil_test(chat_id)
        return
    
    q = questions[q_num]
    buttons = [[{"text": f"{i+1}. {opt}"}] for i, opt in enumerate(q["options"])]
    buttons.append([{"text": "🚫 Прервать тест"}])
    keyboard = {"keyboard": buttons, "resize_keyboard": True}
    send_message(chat_id, f"📝 <b>Вопрос {q_num + 1} из {len(questions)}</b>\n\n{q['q']}", keyboard)


def process_oil_answer(chat_id, answer_text):
    """Обработка ответа на тест по маслам"""
    data = user_test_answers.get(chat_id)
    if not data or data.get("type") != "oil":
        return
    
    q_num = data["current"]
    q = data["questions"][q_num]
    
    try:
        answer_num = int(answer_text[0])
    except:
        answer_num = 1
    
    if answer_num == q["correct"]:
        data["correct"] += 1
        send_message(chat_id, f"✅ <b>Правильно!</b>\n\n<i>{q['explanation']}</i>")
    else:
        correct_answer = q["options"][q["correct"] - 1]
        send_message(chat_id, f"❌ <b>Неправильно!</b>\n\nПравильный ответ: {correct_answer}\n\n<i>{q['explanation']}</i>")
    
    data["current"] += 1
    send_oil_question(chat_id)


def finish_oil_test(chat_id):
    """Завершение теста по маслам"""
    data = user_test_answers.get(chat_id)
    if not data:
        return
    
    cycle = data.get("cycle", 1)
    correct = data["correct"]
    total = len(data["questions"])
    score = int(correct / total * 100)
    
    save_test_result(chat_id, "oil", score, total, cycle)
    
    if score >= 80:
        result = "🎉 Отлично! Вы хорошо знаете материалы цикла!"
    elif score >= 60:
        result = "📚 Неплохо! Но стоит повторить материалы цикла."
    else:
        result = "📖 Стоит поучиться! Рекомендуем повторить материалы цикла и пройти тест снова."
    
    buttons = ["📇 Знаешь ли ты", "💰 Как продать", "📖 История на сегодня", "🎯 Сменить цикл", "◀️ Назад к циклу", "🏠 В главное меню"]
    send_keyboard(chat_id, 
        f"✅ <b>Тест цикла {cycle} пройден!</b>\n\n"
        f"Правильных ответов: {correct} из {total}\n"
        f"Результат: {score}%\n\n"
        f"{result}", 
        buttons)
    
    del user_test_answers[chat_id]


def start_final_exam(chat_id):
    """Начать итоговый тест из 20 вопросов"""
    questions = random.sample(OIL_QUESTIONS_FULL, 20)
    user_test_answers[chat_id] = {"current": 0, "correct": 0, "questions": questions, "type": "final"}
    send_final_question(chat_id)


def send_final_question(chat_id):
    """Отправить вопрос итогового теста"""
    data = user_test_answers.get(chat_id)
    if not data or data.get("type") != "final":
        return
    
    q_num = data["current"]
    questions = data["questions"]
    
    if q_num >= len(questions):
        finish_final_exam(chat_id)
        return
    
    q = questions[q_num]
    buttons = [[{"text": f"{i+1}. {opt}"}] for i, opt in enumerate(q["options"])]
    buttons.append([{"text": "🚫 Прервать тест"}])
    keyboard = {"keyboard": buttons, "resize_keyboard": True}
    send_message(chat_id, f"🎓 <b>ИТОГОВЫЙ ТЕСТ | Вопрос {q_num + 1} из {len(questions)}</b>\n\n{q['q']}", keyboard)


def process_final_answer(chat_id, answer_text):
    """Обработка ответа на итоговый тест"""
    data = user_test_answers.get(chat_id)
    if not data or data.get("type") != "final":
        return
    
    q_num = data["current"]
    q = data["questions"][q_num]
    
    try:
        answer_num = int(answer_text[0])
    except:
        answer_num = 1
    
    if answer_num == q["correct"]:
        data["correct"] += 1
        send_message(chat_id, f"✅ <b>Правильно!</b>")
    else:
        correct_answer = q["options"][q["correct"] - 1]
        send_message(chat_id, f"❌ <b>Неправильно!</b>\n\nПравильный ответ: {correct_answer}")
    
    data["current"] += 1
    send_final_question(chat_id)


def finish_final_exam(chat_id):
    """Завершение итогового теста"""
    data = user_test_answers.get(chat_id)
    if not data:
        return
    
    correct = data["correct"]
    total = len(data["questions"])
    score = int(correct / total * 100)
    
    save_test_result(chat_id, "final", score, total)
    
    if score >= 75:
        result = "🎉 <b>ПОЗДРАВЛЯЮ!</b> Вы сдали итоговый экзамен!\n\n📜 Сертификат «Эксперт по подбору масел» выдан!"
    else:
        result = "📚 К сожалению, вы не сдали экзамен. Рекомендуем повторить материалы циклов и попробовать снова."
    
    buttons = ["🎯 Выбрать цикл", "🏠 В главное меню"]
    send_keyboard(chat_id, 
        f"🎓 <b>ИТОГОВЫЙ ЭКЗАМЕН ПРОЙДЕН</b>\n\n"
        f"Правильных ответов: {correct} из {total}\n"
        f"Результат: {score}%\n\n"
        f"{result}", 
        buttons)
    
    del user_test_answers[chat_id]


# ============= ВЕТКА 2: АДАПТАЦИЯ (сокращённо) =============

BURNOUT_TEXT = """
🔥 <b>Профессиональное выгорание</b>

Выгорание не приходит в один день. Оно накапливается.

<b>⚠️ Признаки:</b>
• Клиенты начинают раздражать без причины
• После смены нет сил даже на любимые дела
• Кажется, что твою работу никто не ценит
• Ты чаще огрызаешься или молчишь

<i>Если узнал себя — это не слабость. Это сигнал, что пора что-то менять.</i>
"""

BURNOUT_TIPS = """
💡 <b>3 техники, которые работают прямо на смене:</b>

1️⃣ <b>Правило тишины</b> — после смены не говори ни слова 10 минут.
2️⃣ <b>Смени сценарий</b> — одну неделю работай чуть медленнее.
3️⃣ <b>Напиши себе письмо</b> — «За что я уважаю себя как оператора».
"""

TOXIC_ADVICE = """
⚠️ <b>Что делать с токсичным коллегой:</b>

Не спасай. Не спорь. Переводи в деловое русло.

<b>Фразы-спасатели:</b>
• «Я услышал. Давай вернёмся к задаче»
• «Это вопрос к старшему оператору»
• «Я не буду это обсуждать сейчас, извини»
"""

AUTHORITY_ADVICE = """
📈 <b>Как повысить свой авторитет:</b>

✔ Начни вести чек-лист для новичков
✔ Стань тем, к кому приходят за ответом
✔ Честно говори: «Я не знаю, но сейчас узнаю»
"""

CLIENT_TYPES = {
    "ham": """🤬 <b>Хам</b>

Клиент: «Ты дурак, ничего не понимаешь!»

Твой ответ: «Я слышу ваше недовольство. Я не буду спорить. Чем я могу помочь по факту?»""",
    "victim": """😢 <b>Жертва</b>

Клиент: «Вечно у вас очереди, всё плохо...»

Твой ответ: «Давайте сделаем так, чтобы сейчас стало лучше. Что именно вас беспокоит?»""",
    "manipulator": """🎭 <b>Манипулятор</b>

Клиент: «Вот на прошлой неделе другой оператор сделал так...»

Твой ответ: «Мне жаль, но я не могу так сделать. Если нарушу правила — меня накажут.»"""
}

CHECKLIST = """
✅ <b>Чек-лист роста</b>

✅ Фиксируй 1 нестандартную ситуацию за смену
✅ Учись у старших коллег
✅ Развивай финансовую грамотность
✅ Участвуй в жизни компании
✅ Учись работать с возражениями
"""

CONFIDENCE = """
💪 <b>Как прокачать уверенность</b>

Раз в неделю напоминай себе:
• Я знаю работу лучше любого новичка
• Я имею право на усталость и плохое настроение
• Я не обязан нравиться всем клиентам
• Моя работа требует внимания, а не героизма
"""

ENERGY_TIPS = {
    "30sec": """⏱️ <b>30 секунд между клиентами</b>

1. Закрой глаза
2. Сделай 2 глубоких вдоха
3. Мысленно скажи: «Этот клиент — первый и новый»
4. Открой глаза
5. Уголки губ вверх — улыбка снижает стресс""",
    "anchor": """⚓ <b>Якорь спокойствия</b>

Выбери любой предмет на кассе. В момент стресса коснись его и скажи:
«Стоп. Я здесь, я справлюсь. Это просто работа».""",
    "ritual": """🎯 <b>Ритуал после смены</b>

Выйдя из АЗС, сделай одно физическое действие: сними бейдж, переобуй сменку, вымой руки."""
}

ADAPTATION_TEST = [
    {"q": "За последний месяц были ли смены, после которых ты чувствовал полное опустошение?",
     "options": ["Да", "Нет"],
     "dangerous": ["Да"],
     "explanation": "Опустошение после смены — первый звоночек."},
    {"q": "Ты стал замечать, что клиенты раздражают тебя чаще, чем полгода назад?",
     "options": ["Да, чаще", "Нет, всё как обычно"],
     "dangerous": ["Да, чаще"],
     "explanation": "Раздражение часто связано с усталостью."},
    {"q": "Открыто ли ты говоришь коллегам, если не согласен, или молчишь?",
     "options": ["Говорю открыто", "Чаще молчу"],
     "dangerous": ["Чаще молчу"],
     "explanation": "Постоянное молчание накапливает напряжение."},
    {"q": "Есть ли человек на работе, с которым можно честно сказать «я устал»?",
     "options": ["Да, есть", "Нет", "Не уверен"],
     "dangerous": ["Нет", "Не уверен"],
     "explanation": "Поддержка коллеги — противоядие от выгорания."},
    {"q": "Берёшь ли ты на себя лишнее — подмены, переработки?",
     "options": ["Да, регулярно", "Иногда", "Нет"],
     "dangerous": ["Да, регулярно", "Иногда"],
     "explanation": "Границы — не эгоизм. Учись говорить «нет»."},
    {"q": "После работы есть занятие, которое восстанавливает силы?",
     "options": ["Да, регулярно", "Иногда", "Нет"],
     "dangerous": ["Иногда", "Нет"],
     "explanation": "Даже 20 минут любимого занятия меняют жизнь."},
    {"q": "Как часто ты думаешь о работе в выходной или перед сном?",
     "options": ["Почти каждый день", "Пару раз в неделю", "Редко"],
     "dangerous": ["Почти каждый день"],
     "explanation": "Если мысли мешают отдыхать — нужен ритуал."},
    {"q": "Был ли конфликт, который ты до сих пор прокручиваешь в голове?",
     "options": ["Да, часто вспоминаю", "Да, но уже отпустил", "Нет"],
     "dangerous": ["Да, часто вспоминаю"],
     "explanation": "Прокручивать конфликт — отдавать энергию."},
    {"q": "Чувствуешь ли ты, что твою работу ценят?",
     "options": ["Да", "Скорее нет", "Не задумывался"],
     "dangerous": ["Скорее нет"],
     "explanation": "Отсутствие признания — причина выгорания."},
    {"q": "Как часто ты делаешь что-то хорошее лично для себя?",
     "options": ["Несколько раз в неделю", "Пару раз за месяц", "Ни разу", "Не помню"],
     "dangerous": ["Пару раз за месяц", "Ни разу", "Не помню"],
     "explanation": "Маленькое «для себя» каждый день — необходимость!"}
]


def start_adaptation_test(chat_id):
    """Начать тест на адаптацию"""
    user_test_answers[chat_id] = {"current": 0, "dangerous_count": 0, "type": "adaptation"}
    send_adaptation_question(chat_id)


def send_adaptation_question(chat_id):
    """Отправить вопрос теста адаптации"""
    data = user_test_answers.get(chat_id)
    if not data or data.get("type") != "adaptation":
        return
    
    q_num = data["current"]
    if q_num >= len(ADAPTATION_TEST):
        finish_adaptation_test(chat_id)
        return
    
    q = ADAPTATION_TEST[q_num]
    buttons = [[{"text": opt}] for opt in q["options"]]
    buttons.append([{"text": "🚫 Прервать тест"}])
    keyboard = {"keyboard": buttons, "resize_keyboard": True}
    send_message(chat_id, f"📋 <b>Вопрос {q_num + 1} из {len(ADAPTATION_TEST)}</b>\n\n{q['q']}", keyboard)


def process_adaptation_answer(chat_id, answer):
    """Обработка ответа на тест адаптации"""
    data = user_test_answers.get(chat_id)
    if not data or data.get("type") != "adaptation":
        return
    
    q_num = data["current"]
    q = ADAPTATION_TEST[q_num]
    
    if answer in q["dangerous"]:
        data["dangerous_count"] += 1
    
    send_message(chat_id, f"📝 <i>{q['explanation']}</i>")
    data["current"] += 1
    send_adaptation_question(chat_id)


def finish_adaptation_test(chat_id):
    """Завершение теста адаптации"""
    data = user_test_answers.get(chat_id)
    if not data:
        return
    
    dangerous = data["dangerous_count"]
    
    if dangerous >= 7:
        result = "🔴 <b>Высокий риск выгорания</b>\n\nТебе нужна пауза. Возьми 2-3 выходных."
    elif dangerous >= 4:
        result = "🟡 <b>Зона риска</b>\n\nВнедри ритуал восстановления."
    else:
        result = "🟢 <b>Хороший ресурс</b>\n\nТы управляешь своим состоянием."
    
    buttons = ["🏠 В главное меню", "💪 Личность и адаптация"]
    send_keyboard(chat_id, f"✅ <b>Тест пройден!</b>\n\nТревожных ответов: {dangerous} из {len(ADAPTATION_TEST)}\n\n{result}", buttons)
    del user_test_answers[chat_id]


def handle_card_navigation(chat_id, action):
    """Навигация по карточкам"""
    cycle = user_cycle.get(chat_id, 1)
    cards = get_cards_by_cycle(cycle)
    current = user_card_index.get(chat_id, 0)
    
    if action == "prev":
        current = (current - 1) % len(cards)
    elif action == "next":
        current = (current + 1) % len(cards)
    elif action == "random":
        current = random.randint(0, len(cards) - 1)
    
    user_card_index[chat_id] = current
    show_card(chat_id)


def handle_cases_navigation(chat_id, action):
    """Навигация по кейсам"""
    cycle = user_cycle.get(chat_id, 1)
    cases = get_cases_by_cycle(cycle)
    current = user_cases_index.get(chat_id, 0)
    
    if action == "prev":
        current = (current - 1) % len(cases)
    elif action == "next":
        current = (current + 1) % len(cases)
    elif action == "random":
        current = random.randint(0, len(cases) - 1)
    
    user_cases_index[chat_id] = current
    show_case(chat_id)


def handle_stories_navigation(chat_id, action):
    """Навигация по историям"""
    cycle = user_cycle.get(chat_id, 1)
    stories = get_stories_by_cycle(cycle)
    current = user_stories_index.get(chat_id, 0)
    
    if action == "prev":
        current = (current - 1) % len(stories)
    elif action == "next":
        current = (current + 1) % len(stories)
    elif action == "random":
        current = random.randint(0, len(stories) - 1)
    
    user_stories_index[chat_id] = current
    show_story(chat_id)


# ============= ОБРАБОТКА СООБЩЕНИЙ =============

def process_webhook_message(chat_id, text):
    """Обработка сообщения из вебхука"""
    try:
        logger.info(f"📨 Получено от {chat_id}: {text[:50]}")
        
        # Проверка на активный тест
        if chat_id in user_test_answers:
            data = user_test_answers[chat_id]
            test_type = data.get("type")
            
            if text == "🚫 Прервать тест":
                del user_test_answers[chat_id]
                if test_type == "oil":
                    set_user_cycle(chat_id, user_cycle.get(chat_id, 1))
                elif test_type == "adaptation":
                    handle_adaptation(chat_id)
                else:
                    handle_start(chat_id)
                return
            
            if test_type == "adaptation":
                process_adaptation_answer(chat_id, text)
            elif test_type == "oil":
                process_oil_answer(chat_id, text)
            elif test_type == "final":
                process_final_answer(chat_id, text)
            return
        
        # Обработка обычных команд
        if text == '/start':
            handle_start(chat_id)
        elif text == '/help' or text == '❓ Помощь':
            show_help(chat_id)
        
        # Ветка 1: О компании
        elif text == '🏢 О компании':
            handle_company(chat_id)
        elif text == '📜 История компании':
            send_keyboard(chat_id, COMPANY_HISTORY, ["◀️ В меню компании", "🏠 В главное меню"])
        elif text == '⭐ Миссия и ценности':
            send_keyboard(chat_id, MISSION, ["◀️ В меню компании", "🏠 В главное меню"])
        elif text == '📋 Наши стандарты работы':
            send_keyboard(chat_id, STANDARDS, ["◀️ В меню компании", "🏠 В главное меню"])
        elif text == '📞 Структура и контакты':
            send_keyboard(chat_id, CONTACTS, ["◀️ В меню компании", "🏠 В главное меню"])
        elif text == '◀️ В меню компании':
            handle_company(chat_id)
        
        # Ветка 2: Адаптация
        elif text == '💪 Личность и адаптация':
            handle_adaptation(chat_id)
        elif text == '🔥 Профессиональное выгорание':
            send_keyboard(chat_id, BURNOUT_TEXT, ["❓ Что делать?", "😫 А если уже всё бесит?", "◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '❓ Что делать?':
            send_keyboard(chat_id, BURNOUT_TIPS, ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '😫 А если уже всё бесит?':
            send_keyboard(chat_id, "😫 Возьми 2 выходных подряд.", ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '👥 Я и коллектив сейчас':
            send_keyboard(chat_id, "👥 <b>Я и коллектив сейчас</b>\n\nТы уже давно в коллективе. Но отношения меняются.\n\nСпроси себя честно:\n• Какая у тебя роль — «вечный соглашатель», «скептик» или «надёжный человек»?\n• С кем из коллег легко работать?\n• Кто сливает твою энергию?\n• Берёшь ли ты лишнее?", ["⚠️ Что делать с токсичным коллегой?", "📈 Как повысить авторитет?", "◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '⚠️ Что делать с токсичным коллегой?':
            send_keyboard(chat_id, TOXIC_ADVICE, ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '📈 Как повысить авторитет?':
            send_keyboard(chat_id, AUTHORITY_ADVICE, ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '😤 Сложные клиенты':
            buttons = ["🤬 Хам", "😢 Жертва", "🎭 Манипулятор", "◀️ Назад к адаптации", "🏠 В главное меню"]
            send_keyboard(chat_id, "😤 <b>Сложные клиенты</b>\n\nКлиенты бывают разными. Твоя задача — не перевоспитать, а сохранить ресурс и помочь по факту.\n\nВыберите тип клиента:", buttons)
        elif text == '🤬 Хам':
            send_keyboard(chat_id, CLIENT_TYPES["ham"], ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '😢 Жертва':
            send_keyboard(chat_id, CLIENT_TYPES["victim"], ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '🎭 Манипулятор':
            send_keyboard(chat_id, CLIENT_TYPES["manipulator"], ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '📈 Моя личность + карьера':
            buttons = ["✅ Чек-лист роста", "💪 Как прокачать уверенность?", "◀️ Назад к адаптации", "🏠 В главное меню"]
            send_keyboard(chat_id, "📈 <b>Моя личность + карьера</b>\n\nТы не просто оператор. Ты человек с амбициями и правом на рост.\n\nКуда двигаться дальше?", buttons)
        elif text == '✅ Чек-лист роста':
            send_keyboard(chat_id, CHECKLIST, ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '💪 Как прокачать уверенность?':
            send_keyboard(chat_id, CONFIDENCE, ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '⚡ Энергия смены':
            buttons = ["⏱️ 30 секунд между клиентами", "⚓ Якорь спокойствия", "🎯 Ритуал после смены", "◀️ Назад к адаптации", "🏠 В главное меню"]
            send_keyboard(chat_id, "⚡ <b>Энергия смены</b>\n\nУсталость копится не за смену, а за минуты, которые ты не отдыхал.\n\nВот 3 приёма, которые работают без перерыва:", buttons)
        elif text == '⏱️ 30 секунд между клиентами':
            send_keyboard(chat_id, ENERGY_TIPS["30sec"], ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '⚓ Якорь спокойствия':
            send_keyboard(chat_id, ENERGY_TIPS["anchor"], ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '🎯 Ритуал после смены':
            send_keyboard(chat_id, ENERGY_TIPS["ritual"], ["◀️ Назад к адаптации", "🏠 В главное меню"])
        elif text == '📊 Тест на адаптацию':
            start_adaptation_test(chat_id)
        elif text == '◀️ В меню адаптации':
            handle_adaptation(chat_id)
        elif text == '◀️ Назад к адаптации':
            handle_adaptation(chat_id)
        
        # Ветка 3: Обучение маслам
        elif text == '📚 Обучение маслам':
            handle_oil(chat_id)
        elif text == '🎯 Выбрать цикл':
            select_cycle(chat_id)
        elif text == '🎯 Сменить цикл':
            select_cycle(chat_id)
        elif text == '◀️ Назад к циклу':
            cycle = user_cycle.get(chat_id, 1)
            set_user_cycle(chat_id, cycle)
        elif text == '🎓 Итоговый тест':
            start_final_exam(chat_id)
        
        # Навигация по циклам
        elif text.startswith('1️⃣ Цикл 1') or text == '✅ Цикл 1 (пройден)':
            set_user_cycle(chat_id, 1)
        elif text.startswith('2️⃣ Цикл 2') or text == '✅ Цикл 2 (пройден)':
            set_user_cycle(chat_id, 2)
        elif text.startswith('3️⃣ Цикл 3') or text == '✅ Цикл 3 (пройден)':
            set_user_cycle(chat_id, 3)
        elif text.startswith('4️⃣ Цикл 4') or text == '✅ Цикл 4 (пройден)':
            set_user_cycle(chat_id, 4)
        elif text.startswith('5️⃣ Цикл 5') or text == '✅ Цикл 5 (пройден)':
            set_user_cycle(chat_id, 5)
        elif text.startswith('6️⃣ Цикл 6') or text == '✅ Цикл 6 (пройден)':
            set_user_cycle(chat_id, 6)
        
        # Материалы цикла
        elif text == '📇 Знаешь ли ты':
            user_card_index[chat_id] = 0
            show_card(chat_id)
        elif text == '💰 Как продать':
            user_cases_index[chat_id] = 0
            show_case(chat_id)
        elif text == '📖 История на сегодня':
            user_stories_index[chat_id] = 0
            show_story(chat_id)
        elif text == '📝 Пройти тест цикла':
            start_oil_test(chat_id)
        
        # Навигация по карточкам
        elif text == '◀️ Предыдущая':
            handle_card_navigation(chat_id, "prev")
        elif text == '▶️ Следующая':
            handle_card_navigation(chat_id, "next")
        elif text == '🎲 Случайная':
            handle_card_navigation(chat_id, "random")
        
        # Навигация по кейсам
        elif text == '◀️ Предыдущий':
            handle_cases_navigation(chat_id, "prev")
        elif text == '▶️ Следующий':
            handle_cases_navigation(chat_id, "next")
        elif text == '🎲 Случайный':
            handle_cases_navigation(chat_id, "random")
        
        # Навигация по историям
        elif text == '◀️ Предыдущая история':
            handle_stories_navigation(chat_id, "prev")
        elif text == '▶️ Следующая история':
            handle_stories_navigation(chat_id, "next")
        elif text == '🎲 Случайная история':
            handle_stories_navigation(chat_id, "random")
        
        elif text == '🏠 В главное меню':
            handle_start(chat_id)
        else:
            handle_start(chat_id)
            
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")


# ============= FLASK ВЕБ-СЕРВЕР =============

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """Точка входа для Telegram webhook"""
    try:
        data = request.get_json()
        if 'message' in data:
            message = data['message']
            chat_id = message['chat']['id']
            text = message.get('text', '')
            process_webhook_message(chat_id, text)
        return 'OK', 200
    except Exception as e:
        logger.error(f"Ошибка в webhook: {e}")
        return 'Error', 500


@app.route('/health')
@app.route('/')
def health():
    """Проверка здоровья для Render"""
    return 'Bot is alive!', 200


def setup_webhook():
    """Устанавливает webhook при запуске"""
    if os.getenv('RENDER'):
        server_url = os.getenv('RENDER_EXTERNAL_URL')
        if not server_url:
            logger.warning("RENDER_EXTERNAL_URL не найден")
            return
    else:
        logger.info("Локальный запуск, пропускаем установку webhook")
        return
    
    webhook_url = f"{server_url}/webhook"
    url = f"{BASE_URL}/setWebhook"
    data = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=data)
        result = response.json()
        if result.get('ok'):
            logger.info(f"✅ Webhook установлен: {webhook_url}")
        else:
            logger.error(f"❌ Ошибка: {result}")
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")


# ============= ЗАПУСК =============

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    setup_webhook()
    logger.info(f"🚀 Бот запущен на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
