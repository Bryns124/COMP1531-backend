from base64 import decode
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper import decode_token, validate_token
from src.auth import email_check, duplicate_email_check
"""User has the 5 functions: users_all, user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle
Functions:
    users_all: Returns a list of all users and their associated details
    user_profile: For a valid user, return info on their user_id, email, first name, last name and handle
    user_profile_setname: Update the authorised user's first name and last name
    user_profile_setemail: Update the authorised user's email address
    user_profile_sethandle: Update the authorised user's hand (handle name)
"""

def users_all_v1(token):
    validate_token(token)
    store = data_store.get()

    user_list = []
    for users in store['users']:
        user_list.append(extract_user_details(users))

    return {
        'users': user_list
    }

def extract_user_details(user):
    users = {
        'u_id' : user['u_id'],
        'email': user['e_mail'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
        }
    return users


def user_profile_v1(token, u_id):
    validate_token(token)
    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']

    for users in store['users']:
        if users['u_id'] == u_id:
            user = extract_user_details(users)

    return {
        'user': user
    }

def user_profile_setname_v1(token, name_first, name_last):
    validate_token(token)
    store = data_store.get()
    if not name_length_check(name_first):
        raise InputError("The length of the new first name has to be within 1 and 50 characters inclusive")
    if not name_length_check(name_last):
        raise InputError("The length of the new last name has to be within 1 and 50 characters inclusive")

    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if user['u_id'] == auth_user_id:
            user['name_first'] = name_first
            user['name_last'] = name_last

    return {}


def user_profile_setemail_v1(token, email):
    validate_token(token)
    store = data_store.get()
    if not valid_email(email):
        raise InputError("Email entered is not of valid format or is already in use by another user")

    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if user['u_id'] == auth_user_id:
            user['email'] = email

    return {}


def user_profile_sethandle_v1(token, handle_str):
    validate_token(token)
    store = data_store.get()
    if not valid_handle_string(store, handle_str):
        raise InputError("""
                         The length of the handle is between 3 and 20 characters,
                         or it contains non-alphanumeric characters,
                         or it is already in-use""")

    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if user['u_id'] == auth_user_id:
            user['handle_str'] = handle_str
    return {}





def name_length_check(name):
    if any(len(name) > 50, len(name) < 1):
        return False
    else:
        return True

def valid_email(email):
    if any(not email_check(email), duplicate_email_check(email)):
        return False
    else:
        return True

def valid_handle_string(store, handle_str):
    if any(len(handle_str) > 20, len(handle_str) < 3, handle_str.isalnum(), duplicate_handle(store, handle_str)):
        return False
    else:
        return True

def duplicate_handle(store, handle_str):
    for users in store['users']:
        if handle_str == users['handle_str']:
            return True
    return False

