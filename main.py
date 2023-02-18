''''''
import imapclient
import pprint
imapObj = imapclient.IMAPClient('imap.mail.ru', ssl=True)
imapObj.login('mail', 'password')
pprint.pprint(imapObj.list_folders())
print(imapObj.select_folder('INBOX/2FA'))
print(imapObj.search('UNSEEN'))