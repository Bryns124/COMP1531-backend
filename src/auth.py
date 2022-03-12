'''
Auth has two main functions: register and login

Functions:
    auth_login_v1: logs in a registered user
    auth_register_v1: registers a new user
        create_user: initialises a new user
            create_handle: creates handle for new user
        email_check: checks if email is valid
        duplicate_email_check: checks if email has already been registered.
'''

import re
from src.data_store import data_store
from src.error import InputError


def auth_login_v1(email, password):
    '''
    Logs in a registered user given an email and password

    :param email: the user's email
    :param password: the user's password

    # REMARK: Nested loops for checks like this are yucky
    '''
    store = data_store.get()
    for user in store['users']:
        if user['email'] == email:
            if user['password'] == password:
                return {
                    'auth_user_id': user['u_id']
                }
            raise InputError("Password is incorrect")

    raise InputError("Email does not exist")


def auth_register_v1(email, password, name_first, name_last):
    '''
    Registers in a new user given the email, password, first name and last name.

    :param email: the user's email
    :param password: the user's password
    :name_first: the user's first name
    :name_last: the user's last name
    :return: the user's user ID
    :rtype: dictionary
    '''
    if not email_check(email):
        raise InputError("Email entered is not a valid email")
    if duplicate_email_check(email):
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


def create_user(email, password, name_first, name_last):
    '''
    Initialises the user's details and saves it into data_store.

    :param email: the user's email
    :param password: the user's password
    :name_first: the user's first name
    :name_last: the user's last name
    :return: the user's details
    :rtype: dictionary
    '''
    store = data_store.get()
    new_id = len(store['users']) + 1
    user = {
        'u_id': new_id,
        'email': email,
        'name_first': name_first,
        'name_last': name_last,
        'handle_str': create_handle(name_first, name_last),
        'password': password,
        'channels_owned': [],
        'channels_joined': [],
    }
    store['users'].append(user)
    data_store.set(store)
    return user

def create_handle(name_first, name_last):
    '''
    Creates the user's handle with the first name and last name.
    If the user's handle is more than 20 characters, it is cut off at 20 characters
    If the user's handle already exists, append the handle with the smallest number
    (starting from 0).

    :name_first: the user's first name
    :name_last: the user's last name
    :return: the user's handle
    :rtype: string
    '''
    store = data_store.get()

    handle = name_first.lower() + name_last.lower()
    handle = ''.join(filter(str.isalnum, handle))
    handle = handle[:20]

    i = 0
    for user in store['users']:
        if user['handle_str'] == handle:
            if i == 0:
                handle += str(0)
                i += 1
                continue
            if i == 10:
                handle = handle[:-1] + str(i)
                i += 1
                continue
            if i % 10 == 1 and i > 10:
                handle = handle[:-2] + str(i)
                i += 1
                continue
            if i % 10 == 0:
                handle = handle[:-2] + str(i)
                i += 1
                continue
            handle = handle[:-1] + str(i % 10)
            i += 1

    return handle

###############################################################
##                 Checking functions                        ##
###############################################################


def email_check(email):
    '''
    Checks if the email entered is valid.

    :email: the user's email
    :return: whether the email is valid or not
    :rtype: boolean
    '''
    regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.fullmatch(regex, email))


def duplicate_email_check(email):
    '''
    Checks if the email entered has already been registered.

    :email: the user's email
    :return: whether the email is new or already has been registered
    :rtype: boolean

    # REMARK: This looks buggy, since it will return the first time
    '''
    store = data_store.get()

    for user in store['users']:
        return bool(user['email'] == email)