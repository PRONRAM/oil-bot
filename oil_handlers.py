# oil_handlers.py - обработчики для обучения маслам

from oil_content import OIL_QUESTIONS_FULL, CARDS, CASES, STORIES
import random

def get_cards_by_cycle(cycle):
    """Получить карточки для цикла"""
    cards_per_cycle = 5
    start = (cycle - 1) * cards_per_cycle
    return list(CARDS.values())[start:start + cards_per_cycle]

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
    """Получить вопросы для теста"""
    questions = get_questions_by_cycle(cycle)
    return random.sample(questions, min(count, len(questions)))
