import re
from src.data_store import data_store
from src.error import InputError

store = data_store.get()

def auth_login_v1(email, password):
    global store
    for user in store['users']:
        if user['email'] == email:
            if user['password'] == password:
                return {
                    'auth_user_id': user['u_id']
                }
            else:
                raise InputError("Password is incorrect")
            
    raise InputError("Email does not exist")
    
###############################################################
##                 Checking functions                        ##
###############################################################
def email_check(email):
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if (re.fullmatch(regex, email)):
        return True
    else:
        return False
    
def duplicate_email_check(email):
    global store
    for user in store['users']:
        if user['email'] == email:
            return True
        else:
            return False

def password_check(password):
    global store
    for user in store['users']:
        if user['password'] == password:
            return user
        else:
            return False

