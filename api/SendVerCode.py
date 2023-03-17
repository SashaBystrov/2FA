import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import logging
import secrets
import sqlite3
import hashlib

logging.basicConfig(filename='logfile.log', level=logging.INFO)


def generate_password():
    """Генерация одноразового пароля"""
    # Генерируем 2 случайных числа в шестнадцатеричном формат
    secret_key1 = secrets.token_hex(6)
    secret_key2 = secrets.token_hex(6)
    # Комбинируем два случайных числа в одну строку и
    # хэшируем с помощью SHA-256
    combined_hash = hashlib.sha256((secret_key1 + secret_key2).encode('utf-8')).hexdigest()
    # Получаем 7-значный пароль
    password = int(combined_hash, 16) % 10000000
    return str(password)


def sendverificationcode(email, username):
    """Отправление одноразового пароля на почту"""

    # Получаем одноразовый код из функции generate_password
    verification_code = generate_password()

    # Данные моей почты для отправки писем
    mylogin_mail = 'sa.bystrov2004@mail.ru'
    mypassword_mail = 'X9daFdDL5zC16gWaB4aQ'

    # Создаем объект сообщения
    message = MIMEMultipart()
    message['From'] = mylogin_mail
    message['To'] = email
    message['Subject'] = 'Код подтверждения'
    text = f'Ваш код подтверждения: {verification_code}'
    message.attach(MIMEText(text, 'plain'))

    smpt_server = 'smtp.mail.ru'
    smpt_port = 587
    try:
        # Подключение к серверу и настройка TLS шифрования
        server = smtplib.SMTP(smpt_server, smpt_port)
        server.starttls()
        server.login(mylogin_mail, mypassword_mail)
        server.sendmail(mylogin_mail, email, message.as_string())
        server.quit()

        # Сохраняем пароль в базе данных
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET onepassword = ? WHERE username = ?",
                       (verification_code, username))
        conn.commit()
        conn.close()

        # Записываем информацию об успешной отправке
        logging.info('Код подтверждения был успешно отправлен на адрес %s',
                     email)

    except (socket.gaierror, socket.timeout) as e:
        logging.error('Ошибка подключения к серверу SMTP: %s', e)
    except smtplib.SMTPAuthenticationError as e:
        logging.error('Ошибка аутентификации: %s', e)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused, smtplib.SMTPDataError) as e:
        logging.error('Ошибка доставки сообщения: %s', e)


# Проверка кода
def valid_code(username, ver_code):
    """Проверяем пароль полученный от пользователя """

    # Берем одноразовый код из базы данных
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT onepassword FROM users WHERE username = ?",
                   (username,))
    onepassword = cursor.fetchone()[0]
    conn.commit()
    conn.close()

    # Проверяем код
    if int(onepassword) == int(ver_code):
        return True
    else:
        return False
