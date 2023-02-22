import random
def NewPassword():
    '''Создание нового пароля'''
    Password = ""
    for i in range(4):
        Digit = random.randint(1, 9)
        StrUpper = chr(random.randint(65, 90))
        Password += StrUpper + str(Digit)
    return Password[0:7]

def VerifyPassword(pkod):
    kod = NewPassword()
    if pkod == kod:
        return True
print(NewPassword())
