# oil_handlers.py - обработчики для обучения маслам

import random
from oil_content import CARDS, CASES, STORIES, OIL_QUESTIONS_FULL

def get_cases_by_cycle(cycle):
    """Получить кейсы для цикла (по 4 штуки)"""
    from oil_content import CASES_BY_CYCLE
    return CASES_BY_CYCLE.get(cycle, CASES_BY_CYCLE[1])

def get_cards_by_cycle(cycle):
    """Получить карточки для цикла (по 5 карточек на цикл)"""
    cards_per_cycle = 5
    cards_list = list(CARDS.values())
    start = (cycle - 1) * cards_per_cycle
    end = start + cards_per_cycle
    if start >= len(cards_list):
        return cards_list[-cards_per_cycle:]
    return cards_list[start:end]

def get_questions_by_cycle(cycle):
    """Получить вопросы для цикла"""
    return [q for q in OIL_QUESTIONS_FULL if q["cycle"] == cycle]

def get_random_cases(count=4):
    """Получить случайные кейсы"""
    return random.sample(CASES, min(count, len(CASES)))

def get_random_stories(count=3):
    """Получить случайные истории"""
    return random.sample(STORIES, min(count, len(STORIES)))

def get_test_questions(cycle, count=5):
    """Получить вопросы для теста по циклу"""
    questions = get_questions_by_cycle(cycle)
    return random.sample(questions, min(count, len(questions)))

def get_all_cycles_info():
    """Получить информацию о всех циклах"""
    cycles = []
    for cycle_num in range(1, 7):
        questions_count = len(get_questions_by_cycle(cycle_num))
        cycles.append({
            "number": cycle_num,
            "questions": questions_count,
            "cards": 5
        })
    return cycles

def get_random_card():
    """Получить случайную карточку"""
    cards_list = list(CARDS.values())
    return random.choice(cards_list)

def get_next_card_index(current_index):
    """Получить следующий индекс карточки (для последовательного просмотра)"""
    cards_list = list(CARDS.values())
    return (current_index + 1) % len(cards_list)

def get_total_cards_count():
    """Получить общее количество карточек"""
    return len(CARDS)

def get_total_cases_count():
    """Получить общее количество кейсов"""
    return len(CASES)

def get_total_stories_count():
    """Получить общее количество историй"""
    return len(STORIES)
