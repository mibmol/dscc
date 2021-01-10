import random
import string

def getPassword():
    minus = 4
    mayus = 4
    numeros = 2 
    longitud = minus + mayus + numeros
    run = True 
    while run:
        caract = string.ascii_letters + string.digits
        contra = ("").join(random.choice(caract) for i in range(longitud))
        if(sum(c.islower() for c in contra) >= minus
            and sum(c.isupper() for c in contra) >= mayus
            and sum(c.isdigit() for c in contra) >= numeros):
            return contra
    return None
    
