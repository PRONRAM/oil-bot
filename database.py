from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional, Dict, List
import json

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False} if 'sqlite' in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    registered_at = Column(DateTime, default=datetime.utcnow)
    
    # Для ветки обучения маслам
    learning_cycle = Column(Integer, default=1)  # Текущий цикл 1-6
    learning_day = Column(Integer, default=1)    # День в цикле
    last_message_at = Column(DateTime, nullable=True)
    exam_passed = Column(Boolean, default=False)
    exam_score = Column(Float, default=0.0)
    
    # Для хранения ответов на тесты
    test_answers = Column(Text, default='{}')  # JSON
    
    def get_test_answers(self) -> Dict:
        return json.loads(self.test_answers)
    
    def set_test_answer(self, question_num: int, answer: str):
        answers = self.get_test_answers()
        answers[str(question_num)] = answer
        self.test_answers = json.dumps(answers)

# Создаем таблицы
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user(db: Session, telegram_id: int) -> Optional[User]:
    return db.query(User).filter(User.telegram_id == telegram_id).first()

def create_user(db: Session, telegram_id: int, username: str = None, first_name: str = None, last_name: str = None) -> User:
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def update_user_learning_progress(db: Session, telegram_id: int, cycle: int = None, day: int = None):
    user = get_user(db, telegram_id)
    if user:
        if cycle is not None:
            user.learning_cycle = cycle
        if day is not None:
            user.learning_day = day
        user.last_message_at = datetime.utcnow()
        db.commit()
