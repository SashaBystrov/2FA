import smtplib
import pyotp
import time
def OtpravkaMail(kmail, kod):
    '''Отправление сообщения на почту'''
    # Подключение к серверу и настройка TLS шифрования
    smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    # Вход в учетную запись
    smtpObj.login('почта', 'пароль')
    # Отправка письма
    smtpObj.sendmail('от кого отправить', kmail , kod )
    # Разрыв соединения
    smtpObj.quit()

if __name__ == '__main__':
    while True:
        # Создание кода для 2FA
        kod = pyotp.random_base32()
        OtpravkaMail(kmail, kod)
