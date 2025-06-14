import sqlite3
import os
import hashlib
from contextlib import contextmanager
import logging
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger(__name__)
DB_PATH = "morse_app.db"

def init_db():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    conn = None
    try:
        # Create a new connection for initialization
        conn = sqlite3.connect(DB_PATH)
        db = conn.cursor()
        
        # Create tables
        db.execute('''
            CREATE TABLE IF NOT EXISTS morse_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal TEXT NOT NULL,
                morse TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                date_of_birth DATE NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            )
        ''')

        db.execute('''
            CREATE TABLE IF NOT EXISTS login_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT
            )
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

@contextmanager
def get_db():
    """إدارة الاتصال بقاعدة البيانات"""
    if not os.path.exists(DB_PATH):
        init_db()
    
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        yield conn.cursor()
        conn.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

def add_morse_signal(signal, morse):
    """إضافة إشارة مورس جديدة"""
    with get_db() as db:
        db.execute(
            'INSERT INTO morse_history (signal, morse) VALUES (?, ?)',
            (signal, morse)
        )

def get_morse_history(limit=10):
    """جلب آخر إشارات المورس"""
    with get_db() as db:
        return db.execute(
            'SELECT * FROM morse_history ORDER BY timestamp DESC LIMIT ?',
            (limit,)
        ).fetchall()

def add_user(email: str, password: str, first_name: str, last_name: str, date_of_birth: str, is_admin: bool = False):
    """إضافة مستخدم جديد"""
    with get_db() as db:
        try:
            # تشفير كلمة المرور باستخدام bcrypt
            hashed_password = pwd_context.hash(password)
            db.execute(
                'INSERT INTO users (email, password, first_name, last_name, date_of_birth, is_admin) VALUES (?, ?, ?, ?, ?, ?)',
                (email, hashed_password, first_name, last_name, date_of_birth, is_admin)
            )
            return True
        except sqlite3.IntegrityError:
            return False

def get_user_by_email(email: str):
    """البحث عن مستخدم باستخدام البريد الإلكتروني"""
    with get_db() as db:
        user = db.execute(
            'SELECT * FROM users WHERE email = ?',
            (email,)
        ).fetchone()
        return dict(user) if user else None

def verify_user(email: str, password: str):
    """التحقق من صحة بيانات تسجيل الدخول"""
    user = get_user_by_email(email)
    if user and pwd_context.verify(password, user['password']):
        return user
    return None

def log_login_attempt(email: str, success: bool, ip_address: str = None):
    """تسجيل محاولة تسجيل الدخول"""
    with get_db() as db:
        db.execute(
            'INSERT INTO login_history (email, success, ip_address) VALUES (?, ?, ?)',
            (email, success, ip_address)
        )

def get_login_history(email: str, limit: int = 5):
    """جلب سجل محاولات تسجيل الدخول"""
    with get_db() as db:
        return db.execute(
            'SELECT * FROM login_history WHERE email = ? ORDER BY timestamp DESC LIMIT ?',
            (email, limit)
        ).fetchall()
