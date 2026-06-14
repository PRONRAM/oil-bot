# oil_handlers.py - обработчики для обучения маслам

import random
from oil_content import CARDS_BY_CYCLE, CASES_BY_CYCLE, STORIES_BY_CYCLE, OIL_QUESTIONS_FULL

def get_cards_by_cycle(cycle):
    """Получить карточки для цикла (по 5 карточек на цикл)"""
    return CARDS_BY_CYCLE.get(cycle, CARDS_BY_CYCLE[1])

def get_cases_by_cycle(cycle):
    """Получить кейсы для цикла (по 4 кейса на цикл)"""
    return CASES_BY_CYCLE.get(cycle, CASES_BY_CYCLE[1])

def get_stories_by_cycle(cycle):
    """Получить истории для цикла (по 3 истории на цикл)"""
    return STORIES_BY_CYCLE.get(cycle, STORIES_BY_CYCLE[1])

def get_questions_by_cycle(cycle):
    """Получить вопросы для цикла (по 8 вопросов на цикл)"""
    return [q for q in OIL_QUESTIONS_FULL if q["cycle"] == cycle]

def get_test_questions(cycle, count=8):
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
    all_cards = [card for cards in CARDS_BY_CYCLE.values() for card in cards]
    return random.choice(all_cards)

def get_random_case():
    """Получить случайный кейс"""
    all_cases = [case for cases in CASES_BY_CYCLE.values() for case in cases]
    return random.choice(all_cases)

def get_random_story():
    """Получить случайную историю"""
    all_stories = [story for stories in STORIES_BY_CYCLE.values() for story in stories]
    return random.choice(all_stories)

def get_total_cards_count():
    """Получить общее количество карточек"""
    return sum(len(cards) for cards in CARDS_BY_CYCLE.values())

def get_total_cases_count():
    """Получить общее количество кейсов"""
    return sum(len(cases) for cases in CASES_BY_CYCLE.values())

def get_total_stories_count():
    """Получить общее количество историй"""
    return sum(len(stories) for stories in STORIES_BY_CYCLE.values())
