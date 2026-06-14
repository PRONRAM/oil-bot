import os
import requests
import json
import time
import logging
import random
import threading
from flask import Flask

def check_cycle_completion(chat_id, cycle):
    """
    Проверяет, все ли материалы цикла просмотрены.
    Возвращает True, если карточки, кейсы и истории просмотрены.
    """
    # Получаем прогресс пользователя по этому циклу
    progress = user_progress.get(chat_id, {}).get(cycle, {})
    
    # Проверяем, что все три материала отмечены как просмотренные
    cards_done = progress.get("cards", False)
    cases_done = progress.get("cases", False)
    stories_done = progress.get("stories", False)
    
    return cards_done and cases_done and stories_done


def mark_material_viewed(chat_id, cycle, material):
    """
    Отмечает, что материал просмотрен.
    material может быть: "cards", "cases", "stories"
    """
    # Создаём структуру, если её нет
    if chat_id not in user_progress:
        user_progress[chat_id] = {}
    
    if cycle not in user_progress[chat_id]:
        user_progress[chat_id][cycle] = {"cards": False, "cases": False, "stories": False}
    
    # Отмечаем конкретный материал как просмотренный
    user_progress[chat_id][cycle][material] = True
    
    # Проверяем, все ли материалы теперь просмотрены
    if check_cycle_completion(chat_id, cycle):
        # Если всё просмотрено — показываем сообщение и кнопку теста
        buttons = ["📝 Пройти тест цикла", "🎯 Выбрать другой цикл", "🏠 В главное меню"]
        send_keyboard(
            chat_id, 
            f"🎉 <b>Поздравляю! Цикл {cycle} полностью пройден!</b>\n\n"
            f"✅ Вы изучили все карточки\n"
            f"✅ Вы изучили все кейсы\n"
            f"✅ Вы прочитали все истории\n\n"
            f"📝 Теперь вам доступен тест по этому циклу!",
            buttons
        )

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
    buttons = ["📇 Знаешь ли ты", "💰 Как продать", "📖 История на сегодня", "🎯 Выбрать цикл", "🏠 В главное меню"]
    welcome_text = """🛢 <b>Готов стать профессионалом в масляной сфере?</b>

Я подготовил тебе <b>6 циклов простого обучения</b>.

📖 Узнавай увлекательные факты
📄 Интересную информацию про масла
💰 Помощь в работе с возражениями
📃 Подведём итоги твоих знаний тестами

<b>Выбирай цикл и полетели!</b> 😉"""
    send_keyboard(chat_id, welcome_text, buttons)

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
    """Начать тест по маслам из текущего цикла (только если материалы просмотрены)"""
    cycle = user_cycle.get(chat_id, 1)
    
    # ========== ПРОВЕРКА ДОСТУПА К ТЕСТУ ==========
    if not check_cycle_completion(chat_id, cycle):
        # Показываем, какие материалы остались непросмотренными
        progress = user_progress.get(chat_id, {}).get(cycle, {})
        missing = []
        if not progress.get("cards", False):
            missing.append("📇 Знаешь ли ты (карточки)")
        if not progress.get("cases", False):
            missing.append("💰 Как продать (кейсы)")
        if not progress.get("stories", False):
            missing.append("📖 История на сегодня")
        
        missing_text = "\n".join(missing)
        send_keyboard(
            chat_id,
            f"🔒 <b>Тест цикла {cycle} пока недоступен!</b>\n\n"
            f"Сначала изучите все материалы этого цикла:\n\n{missing_text}\n\n"
            f"После просмотра всех материалов тест откроется автоматически.",
            ["◀️ В меню обучения"]
        )
        return
    # ============================================
    
    questions = get_test_questions(cycle, count=8)  # 8 вопросов, как в сценарии
    
    if not questions:
        questions = random.sample(OIL_QUESTIONS_FULL, 8)
    
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
    
    # ========== НОВЫЙ КОД ==========
    # Если пользователь просмотрел последнюю карточку, отмечаем цикл
    if idx == total - 1:
        mark_material_viewed(chat_id, cycle, "cards")
    # ================================
    
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
    """Показать кейс из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    cases_list = get_cases_by_cycle(cycle)  # Нужно создать эту функцию
    
    if not cases_list:
        cases_list = CASES[:4]
    
    idx = user_cases_index.get(chat_id, 0)
    
    if idx >= len(cases_list):
        idx = 0
        user_cases_index[chat_id] = 0
    
    case = cases_list[idx]
    total = len(cases_list)
    
    case_text = f"<b>Кейс {idx + 1} из {total}</b>\n\n📌 <b>Ситуация:</b>\n{case['text']}\n\n✅ <b>Правильный ответ:</b>\n{case['answer']}"
    
    # ========== НОВЫЙ КОД ==========
    # Если пользователь просмотрел последний кейс, отмечаем цикл
    if idx == total - 1:
        mark_material_viewed(chat_id, cycle, "cases")
    # ================================
    
    buttons = ["◀️ Предыдущий", "▶️ Следующий", "🎲 Случайный", "🎯 Сменить цикл", "◀️ В меню обучения"]
    send_keyboard(chat_id, f"💰 <b>Как продать? Цикл {cycle}</b>\n\n{case_text}", buttons)

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
    """Показать историю из текущего цикла"""
    cycle = user_cycle.get(chat_id, 1)
    stories_list = get_stories_by_cycle(cycle)
    
    idx = user_stories_index.get(chat_id, 0)
    
    if idx >= len(stories_list):
        idx = 0
        user_stories_index[chat_id] = 0
    
    story = stories_list[idx]
    total = len(stories_list)
    
    # ========== НОВЫЙ КОД ==========
    # Если пользователь просмотрел последнюю историю, отмечаем цикл
    if idx == total - 1:
        mark_material_viewed(chat_id, cycle, "stories")
    # ================================
    
    buttons = ["◀️ Предыдущая", "▶️ Следующая", "🎲 Случайная", "🎯 Сменить цикл", "◀️ В меню обучения"]
    send_keyboard(chat_id, f"📖 <b>Цикл {cycle} | История {idx + 1} из {total}</b>\n\n{story}", buttons)

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
    """Показать меню выбора цикла с отображением прогресса"""
    buttons = []
    
    for cycle_num in range(1, 7):
        # Проверяем, пройден ли этот цикл
        if check_cycle_completion(chat_id, cycle_num):
            # Пройденный цикл — с галочкой
            buttons.append(f"✅ Цикл {cycle_num} (пройден)")
        else:
            # Непройденный цикл
            buttons.append(f"{cycle_num}️⃣ Цикл {cycle_num}")
    
    buttons.append("◀️ В меню обучения")
    
    # Считаем, сколько циклов пройдено
    completed_count = sum(1 for c in range(1, 7) if check_cycle_completion(chat_id, c))
    
    status_text = f"🎯 <b>Выбор цикла обучения</b>\n\n"
    status_text += f"📊 Пройдено циклов: {completed_count} из 6\n\n"
    
    if completed_count == 6:
        status_text += "🏆 <b>Вы прошли все циклы! Доступен итоговый тест!</b>\n\n"
        buttons.insert(0, "🎓 Итоговый тест")
    
    current = user_cycle.get(chat_id, 1)
    status_text += f"📍 Текущий цикл: {current}\n\n"
    status_text += f"Выберите цикл для изучения:"
    
    send_keyboard(chat_id, status_text, buttons)
    
def set_user_cycle(chat_id, cycle):
    """Установить цикл пользователя и показать меню"""
    user_cycle[chat_id] = cycle
    
    # Проверяем, какие материалы уже просмотрены в этом цикле
    progress = user_progress.get(chat_id, {}).get(cycle, {})
    
    # Формируем сообщение о прогрессе
    status_parts = []
    if progress.get("cards", False):
        status_parts.append("✅ Карточки изучены")
    else:
        status_parts.append("❌ Карточки не изучены")
    
    if progress.get("cases", False):
        status_parts.append("✅ Кейсы изучены")
    else:
        status_parts.append("❌ Кейсы не изучены")
    
    if progress.get("stories", False):
        status_parts.append("✅ Истории изучены")
    else:
        status_parts.append("❌ Истории не изучены")
    
    status_text = f"📚 <b>Цикл {cycle}</b>\n\n"
    status_text += "\n".join(status_parts)
    status_text += f"\n\n<b>Доступные материалы:</b>\n"
    status_text += f"📇 Знаешь ли ты — карточки для изучения\n"
    status_text += f"💰 Как продать — кейсы с клиентами\n"
    status_text += f"📖 История на сегодня — интересные факты"
    
    # Проверяем, можно ли уже проходить тест
    if check_cycle_completion(chat_id, cycle):
        status_text += f"\n\n🎓 Тест по циклу {cycle} доступен!"
        buttons = ["📇 Знаешь ли ты", "💰 Как продать", "📖 История на сегодня", "📝 Пройти тест цикла", "🎯 Выбрать другой цикл", "🏠 В главное меню"]
    else:
        buttons = ["📇 Знаешь ли ты", "💰 Как продать", "📖 История на сегодня", "🎯 Выбрать другой цикл", "🏠 В главное меню"]
    
    send_keyboard(chat_id, status_text, buttons)
    
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

   💡 При задержке ответа: бот «засыпает». Подождите 15-30 секунд.
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
        elif text == '❓ Помощь':
            show_help(chat_id)
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
            
# ============= ВЕБ-СЕРВЕР ДЛЯ RENDER =============

app = Flask(__name__)

@app.route('/')
@app.route('/health')
def health_check():
    return "Bot is alive!", 200

def run_web_server():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

# ============= ЗАПУСК =============

if __name__ == '__main__':
    # Запускаем веб-сервер в фоновом потоке
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    # Запускаем основную функцию бота
    main()
if __name__ == '__main__':
    main()
