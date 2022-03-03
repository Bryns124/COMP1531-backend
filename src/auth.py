import re
from src.data_store import data_store
from src.error import InputError

def auth_login_v1(email, password):
    if email_check(email) == False:
        raise InputError
    if duplicate_email_check(email) == False:
        raise InputError
    if password_check(password) == False:
        raise InputError
    
    return {
        'auth_user_id': 1,
    }
    
def auth_register_v1(email, password, name_first, name_last):
    if email_check(email) == False:
        raise InputError("Email entered is not a valid email")
    if duplicate_email_check(email) == True:
        raise InputError("Email entered has already been registered")
    if len(password) < 6:
        raise InputError("Password entered must be longer than 6 characters")
    if len(name_first) < 1 and len(name_first) > 50:
        raise InputError("First name entered must be between 1 and 50 characters inclusive")
    if len(name_last) < 1 and len(name_last) > 50:
        raise InputError("Last name entered must be between 1 and 50 characters inclusive")
    
    user = add_user(email, password, name_first, name_last)
    store = data_store.get()
    store['users'] = []
    store['users'].append(user)
    data_store.set(store)
    print(store)
    return {
        'auth_user_id': 1,
    }

# need to be able to actually create a user but not sure how for now
def create_user(u_id, email, password, name_first, name_last):
    user = {
        'u_id' : u_id,
        'email' : email, 
        'password' : password,
        'name_first' : name_first, 
        'name_last' : name_last, 
        'handle_str' : [],
    } 
    return user

def add_user(email, password, name_first, name_last):
    pass
###############################################################
##                 Checking functions                        ##
###############################################################
def email_check(email):
    regex = r'[A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,3}+'
    if (re.search(regex, email)):
        return True
    else:
        return False
    
def duplicate_email_check(email):
    store = data_store.get()
    for user in store['users']:
        if user['email'] == email:
            return True
        else:
            return False

def password_check(password):
    store = data_store.get()
    for user in store['users']:
        if user['password'] == password:
            return user
        else:
            return False
