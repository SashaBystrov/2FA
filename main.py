# Стандартные библиотеки
from datetime import datetime, timedelta
import logging
import re
import secrets
import sqlite3
import time
# Сторонние библиотеки
from flask import Flask, g, request, render_template, redirect, url_for, session
import pytz
# Модули текущего проекта
from SendVerCode import sendverificationcode, valid_code


logging.basicConfig(filename='logfile.log', level=logging.ERROR,
                    format='%(asctime)s %(message)s', filemode='w')

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DATABASE = 'database.db'


def get_db():
    """Получение соединения с базой данных.
       Защита от SQL-инъекций."""
    db = getattr(g, '_database', None)
    if db is None:
        try:
            db = g._database = sqlite3.connect(DATABASE)
        except sqlite3.Error as e:
            logging.error('Ошибка при подключении к базе данных', e)
            raise e
    return db


@app.teardown_appcontext
def close_db(error):
    """Проверяет, существует ли соединение с базой данных,
       и закрывает его после обработки запроса."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def init_db():
    """Функция создает таблицу users в базе
       данных SQLite, если она еще не существует."""
    with app.app_context():
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         username TEXT NOT NULL,
                         email TEXT NOT NULL,
                         password TEXT NOT NULL,
                         fa INTEGER DEFAULT 0,
                         onepassword INTEGER DEFAULT 0 )''')
            db.commit()
        except sqlite3.Error as e:
            logging.error('Ошибка при создании таблицы в базе данных SQLite', e)
            raise e


def query_db(query, args=(), one=False):
    """Функция выполняет SQL-запрос к базе данных, используя соединение,
    полученное из функции get_db().Запрос выполняется с помощью метода execute(),
    который принимает два параметра: запрос SQL и список аргументов.
    Если запрос успешно выполнен, то функция fetchall() получает все строки результата и
    возвращает их в виде списка кортежей.
    """
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(query, args)
        rv = cursor.fetchall()
        cursor.close()
        return (rv[0] if rv else None) if one else rv
    except sqlite3.Error as e:
        logging.error('Ошибка при выполнении запроса в базе данных SQLite')
        raise e


def generate_token():
    # Генерация токена
    return secrets.token_hex(16)


def get_user_id(username):
    # Возвращение id пользователя по никнейму
    result = query_db("SELECT id FROM users WHERE username = ?", (username,), one=True)
    return result[0]


@app.route('/')
def index():
    # Главная страница
    return render_template('index.html')


@app.route('/register', methods=['POST'])
def registration():
    """Регистрация пользователя"""

    # Берем данные из формы в html
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']

    # Проверяем данные  по шаблонам
    if not re.match(r'^\S+@\S+\.\S{2,}$', email):
        return 'Error! Неправильный формат электронной почты! Формат: X...X@Y...Y', 400
    elif not re.match(r'^[a-zA-Z0-9]{5,}$', username):
        return 'Error! Неправильный формат имени пользователя!', 400
    elif not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$', password):
        return 'Error! Неправильный формат пароля!', 400
    try:
        # Проверем, есть ли пользователь в базе данных
        if query_db('SELECT * FROM users WHERE username = ? OR email = ?', (username, email)):
            return 'Error! Пользователь с этим именем или почтой уже зарегистрирован!', 400
        else:
            # Вставляем данные пользователя в базу данных SQLite
            db = get_db()
            cursor = db.cursor()
            cursor.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                           (username, email, password))
            db.commit()
            cursor.close()

            return redirect(url_for('login'))

    except sqlite3.Error as e:
        logging.error('Ошибка при обработке данных в базе данных SQLite')
        raise e


@app.route('/login', methods=['POST', 'GET'])
def login():
    """Вход в систему"""

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Проверяем существует ли пользователь в базе данных и проверяем пароль
        user = query_db('SELECT id FROM users WHERE username = ? AND password = ?',
                        (username, password), one=True)
        if not user:
            return 'Неправильный логин или пароль', 400

        # Проверяем включена ли 2fa у пользователя
        user_fa = query_db('SELECT fa FROM users WHERE username = ?', [username], one=True)[0]
        email_fa = query_db('SELECT email FROM users WHERE username = ?', [username], one=True)[0]

        session['user_id'] = get_user_id(username)

        if user_fa == 1:
            # Генерируем и отправляем код на почту
            SendVerificationCode(email_fa, username)
            return redirect(url_for('fa2'))

        # Создаем запись о новой сессии
        session['token'] = secrets.token_hex(16)
        session['expires'] = datetime.now() + timedelta(hours=3)

        return redirect(url_for('home'))
    else:
        return render_template('login.html')


@app.route('/fa2', methods=['POST', 'GET'])
def fa2():
    """Двухфакторная аутентификация"""

    # Берем данные из сессии и базы данных
    user_id = session['user_id']

    result = query_db("SELECT username, email FROM users WHERE id = ? ", (user_id,), one=True)
    username = result[0]
    email = result[1]

    code_sent = False

    if request.method == 'POST':
        # Получаем код из формы в html
        ver_code = request.form['ver_code']

        if request.form['submit_button'] == 'retry_code':
            time.sleep(15)
            SendVerificationCode(email, username)

            code_sent = True

        elif request.form['submit_button'] == 'submit':
            if ValidCode(username, ver_code):
                # Создаем сессию
                session['token'] = secrets.token_hex(16)
                session['expires'] = datetime.now() + timedelta(hours=3)
                session['user_id'] = get_user_id(username)

                return redirect(url_for('home'))
            else:
                return 'Неправильно введен код', 400

    return render_template('fa2.html', code_sent=code_sent)


@app.route('/home', methods=['POST', 'GET'])
def home():
    """Личный кабинет"""

    if 'token' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    expires = session['expires']

    if datetime.now().replace(tzinfo=pytz.UTC) > expires:
        session.pop('token', None)
        session.pop('expires', None)
        session.pop('user_id', None)
        return redirect(url_for('login')), 200

    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        if request.form['submit_button'] == 'Подключить':
            cursor.execute("UPDATE users SET fa = 1 WHERE id = ?", (user_id,))
            db.commit()
        elif request.form['submit_button'] == 'Отключить':
            cursor.execute("UPDATE users SET fa = 0 WHERE id = ?", (user_id,))
            db.commit()
        cursor.close()

    result = query_db("SELECT username FROM users WHERE id = ?", (user_id,), one=True)
    username = result[0]

    return render_template('home2.html', username=username)


if __name__ == '__main__':
    init_db()
    app.run()
