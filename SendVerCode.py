import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import socket
import logging
import jwt
import client

mylogin_mail = 'sa.bystrov2004@mail.ru'
mypassword_mail = 'X9daFdDL5zC16gWaB4aQ'
verification_code = jwt.decode(client.GeneratePassword(), "secret", algorithm="HS256")
logging.basicConfig(filename='logfile.log', level=logging.INFO)
def SendVerificationCode(email, verification_code):
    '''Отправление одноразового пароля на почту'''
    message = MIMEMultipart() # Создаем объект сообщения
    message['From'] = mylogin_mail # Адрес отправителя
    message['To'] = email # Адрес получателя
    message['Subject'] = 'Код подтверждения' # Тема сообщения

    text = f'Ваш код подтверждения: {verification_code}'
    message.attach(MIMEText(text, 'plain'))

    smpt_server = 'smtp.mail.ru'
    smpt_port = 587
    try:
        # Подключение к серверу и настройка TLS шифрования
        server = smtplib.SMTP(smpt_server, smpt_port)
        server.starttls()
        server.login(mylogin_mail, mypassword_mail) # Вход в учетную запись
        server.sendmail(mylogin_mail, email, message.as_string() ) # Отправка письма
        server.quit() # Разрыв соединения

        # Записываем информацию об успешной отправке
        logging.info('Код подтверждения был успешно отправлен на адрес %s', email)

    except (socket.gaierror, socket.timeout) as e:
        logging.error('Ошибка подключения к серверу SMTP: %s', e)
    except smtplib.SMTPAuthenticationError as e:
        logging.error('Ошибка аутентификации: %s', e)
    except (smtplib.SMTPRecipientsRefused, smtplib.SMTPSenderRefused, smtplib.SMTPDataError) as e:
        logging.error('Ошибка доставки сообщения: %s', e)