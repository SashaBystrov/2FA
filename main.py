'''
import imapclient
import pprint
imapObj = imapclient.IMAPClient('imap.mail.ru', ssl=True)
imapObj.login('mail', 'password')
pprint.pprint(imapObj.list_folders())
print(imapObj.select_folder('INBOX/2FA'))
print(imapObj.search('UNSEEN'))'''

import smtplib
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