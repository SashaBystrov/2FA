import string
import secrets
import jwt

def GeneratePassword():
    '''Генерация безопасного пароля'''
    alphabet = string.ascii_uppercase + string.digits
    verification_code = ''.join(secrets.choice(alphabet) for i in range(7))
    enc_verification_code = jwt.encode({verification_code:""}, "secret", algorithm="HS256") # Шифрование пароля
    return enc_verification_code

