from base64 import decode
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper import decode_token, validate_token
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

    return user_list


def extract_user_details(user):
    users = {
        'u_id' : user['u_id'],
        'email': user['e_mail'],
        'name_first': user['name_first'],
        'name_last': user['name_last'],
        'handle_str': user['handle_str']
        }
    return users

