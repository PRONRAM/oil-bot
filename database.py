# database.py - работа с базой данных PostgreSQL

import os
import psycopg2
from psycopg2.extras import DictCursor
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Получить соединение с базой данных"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        logger.error("❌ DATABASE_URL не найден в переменных окружения!")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к БД: {e}")
        return None


def init_db():
    """Создать таблицы, если их нет"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Таблица пользователей
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id BIGINT PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                registered_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        # Таблица прогресса по циклам
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT REFERENCES users(telegram_id),
                cycle INTEGER NOT NULL,
                cards_done BOOLEAN DEFAULT FALSE,
                cases_done BOOLEAN DEFAULT FALSE,
                stories_done BOOLEAN DEFAULT FALSE,
                test_passed BOOLEAN DEFAULT FALSE,
                test_score INTEGER DEFAULT 0,
                updated_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(telegram_id, cycle)
            )
        ''')
        
        # Таблица результатов тестов
        cur.execute('''
            CREATE TABLE IF NOT EXISTS test_results (
                id SERIAL PRIMARY KEY,
                telegram_id BIGINT REFERENCES users(telegram_id),
                test_type TEXT NOT NULL,
                cycle INTEGER,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT NOW()
            )
        ''')
        
        conn.commit()
        logger.info("✅ База данных инициализирована")
    except Exception as e:
        logger.error(f"❌ Ошибка инициализации БД: {e}")
    finally:
        conn.close()


def save_user(telegram_id, username=None, first_name=None, last_name=None):
    """Сохранить или обновить пользователя"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO users (telegram_id, username, first_name, last_name)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (telegram_id) 
            DO UPDATE SET username = EXCLUDED.username, 
                          first_name = EXCLUDED.first_name,
                          last_name = EXCLUDED.last_name
        ''', (telegram_id, username, first_name, last_name))
        conn.commit()
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения пользователя: {e}")
    finally:
        conn.close()


def get_user_progress(telegram_id):
    """Получить прогресс пользователя по всем циклам"""
    conn = get_db_connection()
    if not conn:
        return {}
    
    try:
        cur = conn.cursor(cursor_factory=DictCursor)
        cur.execute('''
            SELECT cycle, cards_done, cases_done, stories_done, test_passed, test_score
            FROM user_progress
            WHERE telegram_id = %s
        ''', (telegram_id,))
        
        result = cur.fetchall()
        progress = {}
        for row in result:
            progress[row['cycle']] = {
                'cards': row['cards_done'],
                'cases': row['cases_done'],
                'stories': row['stories_done'],
                'test_passed': row['test_passed'],
                'test_score': row['test_score']
            }
        return progress
    except Exception as e:
        logger.error(f"❌ Ошибка получения прогресса: {e}")
        return {}
    finally:
        conn.close()


def update_progress(telegram_id, cycle, material=None, value=True):
    """Обновить прогресс по конкретному материалу"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        
        # Проверяем, есть ли запись для этого пользователя и цикла
        cur.execute('''
            SELECT id FROM user_progress 
            WHERE telegram_id = %s AND cycle = %s
        ''', (telegram_id, cycle))
        
        if cur.fetchone():
            # Обновляем существующую запись
            if material == 'cards':
                cur.execute('''
                    UPDATE user_progress 
                    SET cards_done = %s, updated_at = NOW()
                    WHERE telegram_id = %s AND cycle = %s
                ''', (value, telegram_id, cycle))
            elif material == 'cases':
                cur.execute('''
                    UPDATE user_progress 
                    SET cases_done = %s, updated_at = NOW()
                    WHERE telegram_id = %s AND cycle = %s
                ''', (value, telegram_id, cycle))
            elif material == 'stories':
                cur.execute('''
                    UPDATE user_progress 
                    SET stories_done = %s, updated_at = NOW()
                    WHERE telegram_id = %s AND cycle = %s
                ''', (value, telegram_id, cycle))
        else:
            # Создаём новую запись
            cur.execute('''
                INSERT INTO user_progress (telegram_id, cycle, cards_done, cases_done, stories_done)
                VALUES (%s, %s, %s, %s, %s)
            ''', (telegram_id, cycle, 
                  value if material == 'cards' else False,
                  value if material == 'cases' else False,
                  value if material == 'stories' else False))
        
        conn.commit()
    except Exception as e:
        logger.error(f"❌ Ошибка обновления прогресса: {e}")
    finally:
        conn.close()


def save_test_result(telegram_id, test_type, score, total_questions, cycle=None):
    """Сохранить результат теста"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO test_results (telegram_id, test_type, cycle, score, total_questions)
            VALUES (%s, %s, %s, %s, %s)
        ''', (telegram_id, test_type, cycle, score, total_questions))
        
        # Если это тест цикла, отмечаем в прогрессе
        if test_type == 'oil' and cycle:
            cur.execute('''
                UPDATE user_progress 
                SET test_passed = TRUE, test_score = %s, updated_at = NOW()
                WHERE telegram_id = %s AND cycle = %s
            ''', (score, telegram_id, cycle))
        
        conn.commit()
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения результата теста: {e}")
    finally:
        conn.close()


def get_completed_cycles(telegram_id):
    """Получить список пройденных циклов"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT cycle FROM user_progress 
            WHERE telegram_id = %s AND test_passed = TRUE
            ORDER BY cycle
        ''', (telegram_id,))
        
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        logger.error(f"❌ Ошибка получения пройденных циклов: {e}")
        return []
    finally:
        conn.close()
