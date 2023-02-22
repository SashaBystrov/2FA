import smtplib
import pyotp
import time
import fa
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

def GetPassword():

def main():

if __name__ == 'main':
    kod = fa.NewPassword()
    OtpravkaMail(kod = kod, kmail= '')
    if fa.VerifyPassword(pkod= '') == 0:
        time.sleep(15)
    else:
        print('Пароль верный!!')


