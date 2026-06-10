import os
import requests
import json
import time
import logging
import random

from oil_content import OIL_QUESTIONS_FULL, CARDS, CASES, STORIES
from oil_handlers import get_cards_by_cycle, get_questions_by_cycle, get_random_cases, get_random_stories, get_test_questions

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота
BOT_TOKEN = os.getenv('Bell_Oilik_Bot')

if not BOT_TOKEN:
    logger.error("❌ ОШИБКА: Bell_Oilik_Bot не найден в переменных окружения!")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0

# Хранилище для данных пользователей
user_test_answers = {}
client_index = {}

# ============= КОНТЕНТ ДЛЯ ВЕТКИ 1 (О КОМПАНИИ) =============

COMPANY_MENU = """
🏢 <b>Корпоративный блок</b>

Добро пожаловать! Здесь вы узнаете о компании «Белоруснефть-Гомельоблнефтепродукт» — кто мы, чем живём и куда движемся.

Что вас интересует?

📜 История компании
⭐ Миссия и ценности
📋 Наши стандарты работы
📞 Структура и контакты
🏠 В главное меню
"""

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

Мы работаем по единым стандартам «Белоруснефть», чтобы любой клиент на любой АЗС получал качественный сервис.

<b>4 главных стандарта:</b>

📌 <b>СТАНДАРТ 1 — Чистота и порядок</b>
На территории АЗС всегда чисто. Витрины, касса, форма — всё безупречно.

📌 <b>СТАНДАРТ 2 — Единое приветствие</b>
Каждый клиент слышит: «Добрый день! Чем могу помочь?»

📌 <b>СТАНДАРТ 3 — Компетентность</b>
Если не знаете ответ: «Я уточню у старшего оператора»

📌 <b>СТАНДАРТ 4 — Прощание</b>
«Спасибо за визит! Хорошей дороги!»
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

# ============= КОНТЕНТ ДЛЯ ВЕТКИ 2 (АДАПТАЦИЯ) =============

ADAPTATION_MENU = """
💪 <b>Личность и адаптация</b>

Давай поговорим о тебе. О том, что помогает работать с кайфом, а что выматывает.

Что сейчас беспокоит или мешает?
"""

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

2️⃣ <b>Смени сценарий</b> — одну неделю работай чуть медленнее и спокойнее.

3️⃣ <b>Напиши себе письмо</b> — «За что я уважаю себя как оператора». Найди 3 честных пункта.
"""

BURNOUT_ANGRY = """
😫 <b>Если уже всё бесит:</b>

Возьми <b>2 выходных подряд</b>.

• В первый день — полный отдых без обязательств
• Во второй — вспомни ситуацию, где ты реально помог клиенту
"""

TEAM_TEXT = """
👥 <b>Я и коллектив сейчас</b>

<b>Спроси себя честно:</b>
• Какая у тебя роль — «вечный соглашатель», «скептик» или «надёжный человек»?
• С кем из коллег легко работать?
• Кто сливает твою энергию?
• Берёшь ли ты лишнее — подмены, переработки?
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

✔ Начни вести чек-лист для новичков — даже 5 пунктов
✔ Стань тем, к кому приходят за ответом
✔ Честно говори: «Я не знаю, но сейчас узнаю»
"""

DIFFICULT_CLIENTS_MENU = """
😤 <b>Сложные клиенты</b>

Клиенты бывают разными. Твоя задача — не перевоспитать, а сохранить ресурс.
"""

CLIENT_TYPES = {
    "ham": """🤬 <b>Хам</b>

Клиент: «Ты дурак, ничего не понимаешь!»

Твой ответ: «Я слышу ваше недовольство. Я не буду спорить. Чем я могу помочь по факту?»

Если продолжает хамить: «Я прерываю диалог. Сейчас позову старшего оператора». И отойди на 2 шага.""",

    "victim": """😢 <b>Жертва</b>

Клиент: «Вечно у вас очереди, всё плохо...»

Твой ответ: «Давайте сделаем так, чтобы сейчас стало лучше. Что именно вас беспокоит?»

Не оправдывайся. Переводи в конструктив.""",

    "manipulator": """🎭 <b>Манипулятор</b>

Клиент: «Вот на прошлой неделе другой оператор сделал так...»

Твой ответ: «Мне жаль, но я не могу так сделать. Если нарушу правила — меня накажут. Давайте найдём другой способ»."""
}

CAREER_MENU = """
📈 <b>Моя личность + карьера</b>

Ты не просто оператор. Ты человек с амбициями и правом на рост.
"""

CHECKLIST = """
✅ <b>Чек-лист роста</b>

Что сделать уже сейчас:

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

ENERGY_MENU = """
⚡ <b>Энергия смены</b>

Усталость копится не за смену, а за минуты, которые ты не отдыхал.
"""

ENERGY_TIPS = {
    "30sec": """⏱️ <b>30 секунд между клиентами</b>

1. Закрой глаза
2. Сделай 2 глубоких вдоха
3. Мысленно скажи: «Этот клиент — первый и новый»
4. Открой глаза
5. Уголки губ вверх — улыбка снижает стресс""",

    "anchor": """⚓ <b>Якорь спокойствия</b>

Выбери любой предмет на кассе.

В момент стресса коснись этого предмета и скажи:
«Стоп. Я здесь, я справлюсь. Это просто работа».""",

    "ritual": """🎯 <b>Ритуал после смены</b>

Выйдя из АЗС, сделай одно физическое действие: сними бейдж, переобуй сменку, вымой руки.

Это сигнал мозгу: «Рабочий режим выключен. Я дома»."""
}

# Тест на адаптацию
ADAPTATION_TEST = [
    {"q": "За последний месяц были ли смены, после которых ты чувствовал полное опустошение?",
     "options": ["Да", "Нет"],
     "dangerous": ["Да"],
     "explanation": "Опустошение после смены — первый звоночек."},
    
    {"q": "Ты стал замечать, что клиенты раздражают тебя чаще, чем полгода назад?",
     "options": ["Да, чаще", "Нет, всё как обычно"],
     "dangerous": ["Да, чаще"],
     "explanation": "Раздражение на клиентов часто связано с усталостью."},
    
    {"q": "Открыто ли ты говоришь коллегам, если не согласен, или молчишь ради мира?",
     "options": ["Говорю открыто", "Чаще молчу"],
     "dangerous": ["Чаще молчу"],
     "explanation": "Постоянное молчание накапливает напряжение."},
    
    {"q": "Есть ли человек на работе, с которым можно честно сказать «я устал»?",
     "options": ["Да, есть", "Нет", "Не уверен"],
     "dangerous": ["Нет", "Не уверен"],
     "explanation": "Поддержка коллеги — противоядие от выгорания."},
    
    {"q": "Берёшь ли ты на себя лишнее — подмены, переработки?",
     "options": ["Да, регулярно", "Иногда", "Нет, у меня свои границы"],
     "dangerous": ["Да, регулярно", "Иногда"],
     "explanation": "Границы — не эгоизм. Учись говорить «нет»."},
    
    {"q": "После работы есть занятие, которое восстанавливает силы?",
     "options": ["Да, регулярно", "Иногда", "Нет, времени нет"],
     "dangerous": ["Иногда", "Нет, времени нет"],
     "explanation": "Даже 20 минут любимого занятия меняют качество жизни."},
    
    {"q": "Как часто ты думаешь о работе в выходной или перед сном?",
     "options": ["Почти каждый день", "Пару раз в неделю", "Редко"],
     "dangerous": ["Почти каждый день"],
     "explanation": "Если мысли мешают отдыхать — нужен ритуал после смены."},
    
    {"q": "Был ли конфликт, который ты до сих пор прокручиваешь в голове?",
     "options": ["Да, часто вспоминаю", "Да, но уже отпустил", "Нет"],
     "dangerous": ["Да, часто вспоминаю"],
     "explanation": "Прокручивать конфликт — отдавать энергию."},
    
    {"q": "Чувствуешь ли ты, что твою работу ценят?",
     "options": ["Да, чувствую", "Скорее нет", "Не задумывался"],
     "dangerous": ["Скорее нет"],
     "explanation": "Отсутствие признания — причина выгорания."},
    
    {"q": "Как часто ты делаешь что-то хорошее лично для себя?",
     "options": ["Несколько раз в неделю", "Пару раз за месяц", "Ни разу", "Не помню"],
     "dangerous": ["Пару раз за месяц", "Ни разу", "Не помню"],
     "explanation": "Маленькое «для себя» каждый день — необходимость!"}
]

# Вопросы по маслам

OIL_MATERIALS = """
📖 <b>Учебные материалы по маслам</b>

<b>1. Вязкость</b>
Способность масла оставаться текучим на морозе.

<b>2. Маркировка</b>
• 0W-20, 5W-30 — всесезонные
• Число перед W — пусковая вязкость
• Число после W — рабочая вязкость

<b>3. API классификация</b>
• API S — для бензиновых
• API C — для дизельных

<b>4. Типы масел</b>
• Минеральное — дешёвое
• Полусинтетика — бюджетный вариант
• Синтетика — лучшая защита
"""

# ============= ФУНКЦИИ ОТПРАВКИ =============

def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if reply_markup:
        data["reply_markup"] = reply_markup
    try:
        requests.post(url, json=data, timeout=10)
    except Exception as e:
        logger.error(f"Ошибка: {e}")

def send_keyboard(chat_id, text, buttons):
    keyboard = {"keyboard": [[{"text": btn}] for btn in buttons], "resize_keyboard": True}
    send_message(chat_id, text, keyboard)

# ============= ОБРАБОТЧИКИ =============

def handle_start(chat_id):
    """Главное меню"""    
    keyboard = {"keyboard": [[{"text": "🏢 О компании"}], [{"text": "💪 Личность и адаптация"}], [{"text": "📚 Обучение маслам"}], [{"text": "❓ Помощь"}]], "resize_keyboard": True}
    text = "👋 Добро пожаловать! Я бот компании «Белоруснефть-Гомельоблнефтепродукт». Выберите раздел в меню."
    send_message(chat_id, text, keyboard)

def handle_company(chat_id):
    buttons = ["📜 История компании", "⭐ Миссия и ценности", "📋 Наши стандарты работы", "📞 Структура и контакты", "🏠 В главное меню"]
    send_keyboard(chat_id, COMPANY_MENU, buttons)

def handle_adaptation(chat_id):
    buttons = ["🔥 Профессиональное выгорание", "👥 Я и коллектив сейчас", "😤 Сложные клиенты", "📈 Моя личность + карьера", "⚡ Энергия смены", "📊 Тест на адаптацию", "🏠 В главное меню"]
    send_keyboard(chat_id, ADAPTATION_MENU, buttons)

def handle_oil(chat_id):
    buttons = ["📇 Карточки знаний", "💼 Кейсы", "📖 Истории", "📖 Учебные материалы", "🎯 Выбрать цикл", "📝 Пройти тест", "🏠 В главное меню"]
    send_keyboard(chat_id, "📚 Обучение маслам. Выберите действие:", buttons)

def handle_burnout(chat_id):
    buttons = ["❓ Что делать?", "😫 А если уже всё бесит?", "◀️ В меню адаптации"]
    send_keyboard(chat_id, BURNOUT_TEXT, buttons)

def handle_team(chat_id):
    buttons = ["⚠️ Что делать с токсичным коллегой?", "📈 Как повысить авторитет?", "◀️ В меню адаптации"]
    send_keyboard(chat_id, TEAM_TEXT, buttons)

def handle_difficult_clients(chat_id):
    buttons = ["🤬 Хам", "😢 Жертва", "🎭 Манипулятор", "🔄 Ещё тип клиента", "◀️ В меню адаптации"]
    send_keyboard(chat_id, DIFFICULT_CLIENTS_MENU, buttons)

def handle_career(chat_id):
    buttons = ["✅ Чек-лист роста", "💪 Как прокачать уверенность?", "◀️ В меню адаптации"]
    send_keyboard(chat_id, CAREER_MENU, buttons)

def handle_energy(chat_id):
    buttons = ["⏱️ 30 секунд между клиентами", "⚓ Якорь спокойствия", "🎯 Ритуал после смены", "◀️ В меню адаптации"]
    send_keyboard(chat_id, ENERGY_MENU, buttons)

def start_adaptation_test(chat_id):
    user_test_answers[chat_id] = {"current": 0, "dangerous_count": 0, "type": "adaptation"}
    send_test_question(chat_id)

def send_test_question(chat_id):
    data = user_test_answers.get(chat_id)
    if not data or data["type"] != "adaptation":
        return
    
    q_num = data["current"]
    if q_num >= len(ADAPTATION_TEST):
        finish_adaptation_test(chat_id)
        return
    
    q = ADAPTATION_TEST[q_num]
    buttons = [[{"text": opt}] for opt in q["options"]]
    buttons.append([{"text": "🚫 Прервать тест"}])
    keyboard = {"keyboard": buttons, "resize_keyboard": True}
    send_message(chat_id, f"📋 Вопрос {q_num + 1} из {len(ADAPTATION_TEST)}\n\n{q['q']}", keyboard)

def process_test_answer(chat_id, answer):
    data = user_test_answers.get(chat_id)
    if not data or data["type"] != "adaptation":
        return
    
    q_num = data["current"]
    q = ADAPTATION_TEST[q_num]
    
    if answer in q["dangerous"]:
        data["dangerous_count"] += 1
    
    send_message(chat_id, f"📝 {q['explanation']}")
    data["current"] += 1
    send_test_question(chat_id)

def finish_adaptation_test(chat_id):
    data = user_test_answers.get(chat_id)
    if not data:
        return
    
    dangerous = data["dangerous_count"]
    
    if dangerous >= 7:
        result = "🔴 Высокий риск выгорания. Возьми паузу, 2-3 выходных."
    elif dangerous >= 4:
        result = "🟡 Зона риска. Внедри ритуал восстановления."
    else:
        result = "🟢 Хороший ресурс. Поделись с коллегой."
    
    buttons = ["🏠 В главное меню", "💪 Личность и адаптация"]
    send_keyboard(chat_id, f"✅ Тест пройден! Тревожных ответов: {dangerous} из {len(ADAPTATION_TEST)}\n\n{result}", buttons)
    del user_test_answers[chat_id]

def start_oil_test(chat_id):
    """Начать тест по маслам из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    questions = get_test_questions(cycle, count=5)
    
    if not questions:
        questions = random.sample(OIL_QUESTIONS_FULL, 5)
    
    user_test_answers[chat_id] = {"current": 0, "correct": 0, "questions": questions, "type": "oil", "cycle": cycle}
    send_oil_question(chat_id)

def send_oil_question(chat_id):
    data = user_test_answers.get(chat_id)
    if not data or data["type"] != "oil":
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
    send_message(chat_id, f"📝 Вопрос {q_num + 1} из {len(questions)}\n\n{q['q']}", keyboard)

def process_oil_answer(chat_id, answer_text):
    data = user_test_answers.get(chat_id)
    if not data or data["type"] != "oil":
        return
    
    q_num = data["current"]
    q = data["questions"][q_num]
    
    try:
        answer_num = int(answer_text[0])
    except:
        answer_num = 1
    
    if answer_num == q["correct"]:
        data["correct"] += 1
        send_message(chat_id, f"✅ Правильно! {q['explanation']}")
    else:
        correct_answer = q["options"][q["correct"] - 1]
        send_message(chat_id, f"❌ Неправильно! Правильный ответ: {correct_answer}\n\n{q['explanation']}")
    
    data["current"] += 1
    send_oil_question(chat_id)

def finish_oil_test(chat_id):
    """Завершение теста по маслам"""
    data = user_test_answers.get(chat_id)
    if not data:
        return
    
    correct = data["correct"]
    total = len(data["questions"])
    score = int(correct / total * 100)
    
    if score >= 80:
        result = "🎉 Отлично! Вы хорошо знаете материалы!"
    elif score >= 60:
        result = "📚 Неплохо! Но стоит повторить."
    else:
        result = "📖 Стоит поучиться! Изучите материалы и пройдите тест снова."
    
    buttons = ["📖 Учебные материалы", "📝 Пройти тест (8 вопросов)", "🏠 В главное меню", "◀️ В меню обучения"]
    
    send_keyboard(chat_id, 
        f"✅ Тест пройден!\n\n"
        f"Правильных ответов: {correct} из {total}\n"
        f"Результат: {score}%\n\n"
        f"{result}", 
        buttons)
     
    del user_test_answers[chat_id]

def show_oil_materials(chat_id):
    buttons = ["📝 Пройти тест (8 вопросов)", "🏠 В главное меню"]
    send_keyboard(chat_id, OIL_MATERIALS, buttons)

# ============= КАРТОЧКИ ЗНАНИЙ =============

user_card_index = {}

def show_card(chat_id):
    """Показать карточку из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    
    # Получаем карточки для цикла (5 штук)
    cards_list = get_cards_by_cycle(cycle)
    
    if not cards_list:
        cards_list = list(CARDS.values())[:5]
    
    idx = user_card_index.get(chat_id, 0)
    
    if idx >= len(cards_list):
        idx = 0
        user_card_index[chat_id] = 0
    
    card_text = cards_list[idx]
    total = len(cards_list)
    
    buttons = ["◀️ Предыдущая", "▶️ Следующая", "🎲 Случайная", "🎯 Сменить цикл", "◀️ В меню обучения"]
    send_keyboard(chat_id, f"📇 <b>Цикл {cycle} | Карточка {idx + 1} из {total}</b>\n\n{card_text}", buttons)

def handle_card_navigation(chat_id, action):
    """Обработка навигации по карточкам"""
    if chat_id not in user_card_index:
        user_card_index[chat_id] = 0
    
    cards_list = list(CARDS.values())
    current = user_card_index[chat_id]
    
    if action == "prev":
        current = (current - 1) % len(cards_list)
    elif action == "next":
        current = (current + 1) % len(cards_list)
    elif action == "random":
        current = random.randint(0, len(cards_list) - 1)
    
    user_card_index[chat_id] = current
    show_card(chat_id)
    
# ============= КЕЙСЫ "КАК ПРОДАТЬ" =============

user_cases_index = {}

def show_case(chat_id):
    """Показать текущий кейс"""
    idx = user_cases_index.get(chat_id, 0)
    cases_list = CASES
    
    if idx >= len(cases_list):
        idx = 0
        user_cases_index[chat_id] = 0
    
    case = cases_list[idx]
    case_text = f"<b>Кейс {idx + 1} из {len(cases_list)}</b>\n\n📌 <b>Ситуация:</b>\n{case['text']}\n\n✅ <b>Правильный ответ:</b>\n{case['answer']}"
    total = len(cases_list)
    
    buttons = ["◀️ Предыдущий", "▶️ Следующий", "🎲 Случайный", "◀️ В меню обучения"]
    send_keyboard(chat_id, f"💼 <b>Как продать?</b>\n\n{case_text}", buttons)

def handle_cases_navigation(chat_id, action):
    """Обработка навигации по кейсам"""
    if chat_id not in user_cases_index:
        user_cases_index[chat_id] = 0
    
    cases_list = CASES
    current = user_cases_index[chat_id]
    
    if action == "prev":
        current = (current - 1) % len(cases_list)
    elif action == "next":
        current = (current + 1) % len(cases_list)
    elif action == "random":
        current = random.randint(0, len(cases_list) - 1)
    
    user_cases_index[chat_id] = current
    show_case(chat_id)

# ============= ИСТОРИИ =============

user_stories_index = {}

def show_story(chat_id):
    """Показать текущую историю"""
    idx = user_stories_index.get(chat_id, 0)
    stories_list = STORIES
    
    if idx >= len(stories_list):
        idx = 0
        user_stories_index[chat_id] = 0
    
    story = stories_list[idx]
    total = len(stories_list)
    
    buttons = ["◀️ Предыстория", "▶️ Следующая история", "🎲 Случайная история", "◀️ В меню обучения"]
    send_keyboard(chat_id, f"📖 <b>История {idx + 1} из {total}</b>\n\n{story}", buttons)

def handle_stories_navigation(chat_id, action):
    """Обработка навигации по историям"""
    if chat_id not in user_stories_index:
        user_stories_index[chat_id] = 0
    
    stories_list = STORIES
    current = user_stories_index[chat_id]
    
    if action == "prev":
        current = (current - 1) % len(stories_list)
    elif action == "next":
        current = (current + 1) % len(stories_list)
    elif action == "random":
        current = random.randint(0, len(stories_list) - 1)
    
    user_stories_index[chat_id] = current
    show_story(chat_id)

# ============= ВЫБОР ЦИКЛА =============

user_cycle = {}  # Хранит текущий цикл пользователя (1-6)

def select_cycle(chat_id):
    """Показать меню выбора цикла"""
    buttons = ["1️⃣ Цикл 1 (Вязкость)", "2️⃣ Цикл 2 (API, ACEA)", "3️⃣ Цикл 3 (Типы масел)", "4️⃣ Цикл 4 (Ошибки)", "5️⃣ Цикл 5 (Спецмасла)", "6️⃣ Цикл 6 (Повторение)", "◀️ В меню обучения"]
    current = user_cycle.get(chat_id, 1)
    send_keyboard(chat_id, f"🎯 <b>Выберите цикл обучения</b>\n\nТекущий цикл: {current}\n\nВ каждом цикле:\n• 5 карточек\n• 8 вопросов\n• Промежуточный тест", buttons)

def set_user_cycle(chat_id, cycle):
    """Установить цикл пользователя"""
    user_cycle[chat_id] = cycle
    send_keyboard(chat_id, f"✅ Установлен <b>Цикл {cycle}</b>\n\nТеперь карточки и тест будут из этого цикла.\n\nВыберите действие:", ["📇 Карточки цикла", "📝 Тест цикла", "◀️ В меню обучения"])

def show_help(chat_id):
    """Показать справку"""
    help_text = """
   ❓ <b>Помощь по работе с ботом</b>

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
   • 30 карточек «Знаешь ли ты»
   • 24 кейса «Как продать»
   • 18 историй
   • Тест из 48 вопросов

   <b>📌 Команды:</b>
   /start — главное меню
   /help — эта справка

   💡 При задержке ответа: бот «засыпает» на бесплатном хостинге. Подождите 15-30 секунд.
   """
    buttons = ["🏠 В главное меню"]
    send_keyboard(chat_id, help_text, buttons)

# ============= ОСНОВНОЙ ЦИКЛ =============

def process_message(message):
    try:
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        logger.info(f"Получено: {text[:50]}")
        
        # Проверка на активный тест
        if chat_id in user_test_answers:
            if text == "🚫 Прервать тест":
                del user_test_answers[chat_id]
                handle_start(chat_id)
                return
            
            data = user_test_answers[chat_id]
            if data["type"] == "adaptation":
                process_test_answer(chat_id, text)
            else:
                process_oil_answer(chat_id, text)
            return
        
        # Обработка команд
        if text == '/start':
            handle_start(chat_id)
        elif text == '/help':
            show_help(chat_id)
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
        elif text == '💪 Личность и адаптация':
            handle_adaptation(chat_id)
        elif text == '🔥 Профессиональное выгорание':
            handle_burnout(chat_id)
        elif text == '❓ Что делать?':
            send_keyboard(chat_id, BURNOUT_TIPS, ["◀️ В меню адаптации"])
        elif text == '😫 А если уже всё бесит?':
            send_keyboard(chat_id, BURNOUT_ANGRY, ["◀️ В меню адаптации"])
        elif text == '👥 Я и коллектив сейчас':
            handle_team(chat_id)
        elif text == '⚠️ Что делать с токсичным коллегой?':
            send_keyboard(chat_id, TOXIC_ADVICE, ["◀️ В меню адаптации"])
        elif text == '📈 Как повысить авторитет?':
            send_keyboard(chat_id, AUTHORITY_ADVICE, ["◀️ В меню адаптации"])
        elif text == '😤 Сложные клиенты':
            handle_difficult_clients(chat_id)
        elif text == '🤬 Хам':
            send_keyboard(chat_id, CLIENT_TYPES["ham"], ["◀️ В меню адаптации"])
        elif text == '😢 Жертва':
            send_keyboard(chat_id, CLIENT_TYPES["victim"], ["◀️ В меню адаптации"])
        elif text == '🎭 Манипулятор':
            send_keyboard(chat_id, CLIENT_TYPES["manipulator"], ["◀️ В меню адаптации"])
        elif text == '🔄 Ещё тип клиента':
            types = ["ham", "victim", "manipulator"]
            idx = client_index.get(chat_id, 0)
            send_keyboard(chat_id, CLIENT_TYPES[types[idx]], ["◀️ В меню адаптации"])
            client_index[chat_id] = (idx + 1) % 3
        elif text == '📈 Моя личность + карьера':
            handle_career(chat_id)
        elif text == '✅ Чек-лист роста':
            send_keyboard(chat_id, CHECKLIST, ["◀️ В меню адаптации"])
        elif text == '💪 Как прокачать уверенность?':
            send_keyboard(chat_id, CONFIDENCE, ["◀️ В меню адаптации"])
        elif text == '⚡ Энергия смены':
            handle_energy(chat_id)
        elif text == '⏱️ 30 секунд между клиентами':
            send_keyboard(chat_id, ENERGY_TIPS["30sec"], ["◀️ В меню адаптации"])
        elif text == '⚓ Якорь спокойствия':
            send_keyboard(chat_id, ENERGY_TIPS["anchor"], ["◀️ В меню адаптации"])
        elif text == '🎯 Ритуал после смены':
            send_keyboard(chat_id, ENERGY_TIPS["ritual"], ["◀️ В меню адаптации"])
        elif text == '📊 Тест на адаптацию':
            start_adaptation_test(chat_id)
        elif text == '◀️ В меню адаптации':
            handle_adaptation(chat_id)
        elif text == '📚 Обучение маслам':
            handle_oil(chat_id)
        elif text == '📇 Карточки знаний':
            user_card_index[chat_id] = 0
            show_card(chat_id)
        elif text == '💼 Кейсы':
            user_cases_index[chat_id] = 0
            show_case(chat_id)
        elif text == '📖 Истории':
            user_stories_index[chat_id] = 0
            show_story(chat_id)
        elif text == '◀️ Предыдущая':
            handle_card_navigation(chat_id, "prev")
        elif text == '▶️ Следующая':
            handle_card_navigation(chat_id, "next")
        elif text == '🎲 Случайная':
            handle_card_navigation(chat_id, "random")
        elif text == '◀️ Предыдущий':
            handle_cases_navigation(chat_id, "prev")
        elif text == '▶️ Следующий':
            handle_cases_navigation(chat_id, "next")
        elif text == '🎲 Случайный':
            handle_cases_navigation(chat_id, "random")
        elif text == '◀️ Предыстория':
            handle_stories_navigation(chat_id, "prev")
        elif text == '▶️ Следующая история':
            handle_stories_navigation(chat_id, "next")
        elif text == '🎲 Случайная история':
            handle_stories_navigation(chat_id, "random") 
        elif text == '📖 Учебные материалы':
            show_oil_materials(chat_id)
        elif text == '🎯 Выбрать цикл':
            select_cycle(chat_id)
        elif text == '1️⃣ Цикл 1 (Вязкость)':
            set_user_cycle(chat_id, 1)
        elif text == '2️⃣ Цикл 2 (API, ACEA)':
            set_user_cycle(chat_id, 2)
        elif text == '3️⃣ Цикл 3 (Типы масел)':
            set_user_cycle(chat_id, 3)
        elif text == '4️⃣ Цикл 4 (Ошибки)':
            set_user_cycle(chat_id, 4)
        elif text == '5️⃣ Цикл 5 (Спецмасла)':
            set_user_cycle(chat_id, 5)
        elif text == '6️⃣ Цикл 6 (Повторение)':
            set_user_cycle(chat_id, 6)
        elif text == '📇 Карточки цикла':
            user_card_index[chat_id] = 0
            show_card(chat_id)
        elif text == '📝 Тест цикла':
            start_oil_test(chat_id)
        elif text == '🎯 Сменить цикл':
            select_cycle(chat_id)    
        elif text == '📝 Пройти тест (48 вопросов)':
            start_oil_test(chat_id)
        elif text == '◀️ В меню обучения':
            handle_oil(chat_id)
        elif text == '🏠 В главное меню':
            handle_start(chat_id)
        else:
            handle_start(chat_id)
            
    except Exception as e:
        logger.error(f"Ошибка: {e}")

def main():
    global last_update_id
    logger.info("Бот запущен!")
    
    while True:
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {"offset": last_update_id + 1, "timeout": 30}
            response = requests.get(url, params=params, timeout=35)
            data = response.json()
            
            if data.get('ok'):
                for update in data.get('result', []):
                    last_update_id = update['update_id']
                    if 'message' in update:
                        process_message(update['message'])
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()
