from aiogram.dispatcher.filters.state import State, StatesGroup

class TestStates(StatesGroup):
    # Тест на адаптацию
    ADAPTATION_TEST = State()
    ADAPTATION_Q1 = State()
    ADAPTATION_Q2 = State()
    ADAPTATION_Q3 = State()
    ADAPTATION_Q4 = State()
    ADAPTATION_Q5 = State()
    ADAPTATION_Q6 = State()
    ADAPTATION_Q7 = State()
    ADAPTATION_Q8 = State()
    ADAPTATION_Q9 = State()
    ADAPTATION_Q10 = State()
    
    # Экзамен по маслам
    OIL_EXAM = State()