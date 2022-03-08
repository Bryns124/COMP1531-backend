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

def auth_register_v1(email, password, name_first, name_last):
    if email_check(email) == False:
        raise InputError("Email entered is not a valid email")
    if duplicate_email_check(email) == True:
        raise InputError("Email entered has already been registered")
    if len(password) < 6:
        raise InputError("Password entered must be longer than 6 characters")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError("First name entered must be between 1 and 50 characters inclusive")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError("Last name entered must be between 1 and 50 characters inclusive")

    user = create_user(email, password, name_first, name_last)
    return {
        'auth_user_id': user['u_id']
    }

# need to be able to actually create a user but not sure how for now
def create_user(email, password, name_first, name_last):
    global store
    new_id = len(store['users']) + 1
    user = {
        'u_id' : new_id, 
        'email': email, 
        'name_first': name_first, 
        'name_last': name_last, 
        'handle_str': create_handle(name_first, name_last),
        'password': password,
        'channels_owned' : [], 
        'channels_joined' : [],
    }
    store['users'].append(user)
    data_store.set(store)
    return user

def create_handle(name_first, name_last):
    global store
    
    handle = name_first.lower() + name_last.lower()
    handle = ''.join(filter(str.isalnum, handle))
    handle = handle[:20]
    
    i = 0
    for user in store['users']:
        if user['handle_str'] == handle:
            handle += (str(i))
            i += 1
            
    return handle
    
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