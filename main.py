import smtplib
import pyotp
import time
def OtpravkaMail():
    '''Отправление сообщения на почту'''
    # Подключение к серверу и настройка TLS шифрования
    smtpObj = smtplib.SMTP('smtp.mail.ru', 587)
    smtpObj.ehlo()
    smtpObj.starttls()
    # Вход в учетную запись
    smtpObj.login('почта', 'пароль')
    # Отправка письма
    smtpObj.sendmail('от кого отправить', 'куда отправить', 'Сообщение')
    # Разрыв соединения
    smtpObj.quit()

def GenPassword():
    totp = pyotp.TOTP('base32secret3232')
    print(pyotp.random_base32())
    # OTP verified for current time
    totp.verify('')
    time.sleep(15)

if __name__ == '__main__':
    while True:
        GenPassword()