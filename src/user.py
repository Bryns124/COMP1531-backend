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
    """returns a list of all users and their associated details

    Args:
        token (string): user calling the function

    Raises:
        None

    Returns:
        dictionary: containing list of dictionaries with the details of the users
    """
    store = data_store.get()
    decode_token(token)

    user_list = []
    for users in store['users']:
        user_list.append(extract_user_details(store["users"][users]))

    return {
        'users': user_list
    }


def extract_user_details(user):
    users = {
        'u_id': user.auth_user_id,
        'email': user.email,
        'name_first': user.name_first,
        'name_last': user.name_last,
        'handle_str': user.handle
    }
    return users

def user_profile_v1(token, u_id):
    """returns a the details of one particular user with the associated user_id

    Args:
        token (string): user calling the function
        u_id (int): authorisation user id of the user whose details are required

    Raises:
        InputError: u_id does not refer to a valid user

    Returns:
        dictionary: containing the details of the user's profile
    """
    store = data_store.get()
    decode_token(token)
    valid_user_id(u_id)

    if u_id in store["removed_users"]:
        user_details = extract_user_details(store["removed_users"][u_id])
        return {'user': user_details}

    if u_id in store["users"]:
        user_details = extract_user_details(store["users"][u_id])


    return {
        'user': user_details
    }


def valid_user_id(user_id):
    """_summary_
    Validates that the input auth_user_id exists in the datastore
    Args:
        auth_user_id (u_id): The input u_id

    Raises:
        AccessError: If the u_id input does not exist in the system, an access error is raised.
    """
    store = data_store.get()

    if user_id in store["users"] or user_id in store["removed_users"]:
        return True

    raise InputError(description="This auth_user_id does not exist in the datastore.")


def user_profile_setname_v1(token, name_first, name_last):
    """Updates the authorised user's first and last name
    Args:
        token (string): user who wants their name changed in their profile

    Raises:
        InputError: length of first name is more than 50 character or less than 1 character
        InputError: length of first name is more than 50 character or less than 1 character

    Returns:
        None
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not name_length_check(name_first):
        raise InputError(description=
            "The length of the new first name has to be within 1 and 50 characters inclusive")
    if not name_length_check(name_last):
        raise InputError(description=
            "The length of the new last name has to be within 1 and 50 characters inclusive")

    store["users"][auth_user_id].name_first = name_first
    store["users"][auth_user_id].name_last = name_last
    data_store.set(store)
    return {}


def user_profile_setemail_v1(token, email):
    """Updates the authorised user's email
    Args:
        token (string): user who wants their email changed in their profile

    Raises:
        InputError: email does not follos valid email format
        InputError: email is already in use by another user

    Returns:
        None
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not valid_email(email):
        raise InputError(description=
            "Email entered is not of valid format or is already in use by another user")

    store["users"][auth_user_id].email = email
    data_store.set(store)
    return {}


def user_profile_sethandle_v1(token, handle_str):
    """Updates the authorised user's handle name
    Args:
        token (string): user who wants their handle name changed in their profile

    Raises:
        InputError: length of handle name is not between 3 and 20 characters inclusive
        InputError: handle_str contains characters that are not alphanumeric
        InputError: the handle is already in use by another user

    Returns:
        None
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not valid_handle_string(store, handle_str):
        raise InputError(description="""
                         The length of the handle is between 3 and 20 characters,
                         or it contains non-alphanumeric characters,
                         or it is already in-use""")

    store["users"][auth_user_id].handle = handle_str
    data_store.set(store)
    return {}


def name_length_check(name):
    '''returns True if the length of the name is between 1 and 50 characters inclusive'''
    if len(name) > 50 or len(name) < 1:
        return False
    else:
        return True


def valid_email(email):
    '''returns True if the email follows proper email formatting and is not already in use by another user'''
    if not email_check(email) or duplicate_email_check(email):
        return False
    else:
        return True


def valid_handle_string(store, handle_str):
    '''returns True if all three of the following things are satisfied:
    - length is between 0 and 20 characters
    - is alphanumeric
    - not already in use
    '''
    if len(handle_str) > 20 or len(handle_str) < 3 or not handle_str.isalnum() or duplicate_handle(store, handle_str):
        return False
    else:
        return True


def duplicate_handle(store, handle_str):
    '''returns True if the given handle string is already use'''
    for users in store['users']:
        if handle_str == store["users"][users].handle:
            return True
    return False
