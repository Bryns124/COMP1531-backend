from src.data_store import data_store
from src.error import InputError

def auth_login_v1(email, password):
    store = data_store.get()
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
    return {
        'auth_user_id': 1,
    }

    
