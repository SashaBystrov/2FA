import smtplib
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

def