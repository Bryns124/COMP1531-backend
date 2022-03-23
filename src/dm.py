from base64 import decode
from re import U
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper import decode_token, validate_token
"""Dm has the 7 functions: create, list, remove, details, leave, messages, senddm
Functions:
    dm_create: creates a new dm is created
    dm_list: returns the list of dm's that a user is part of
    dm_remove: remove an existing dm so that all members are no longer in DM.
    dm_details: provide basic details about a particular dm given the dm_id
    dm_leave: user is removed as a member of the DM
    dm_messages: returns upto 50 messsages of the DM associated with the provided dm_id
"""


def dm_create_v1(token, list_of_u_ids):
    """a user creates a dm given a list of u id's
        the creator of the dm is the owner

    Args:
        token (string): creator of the dm
        u_ids (int): users in the dm

    Raises:
        AccessError: if the user doese not exist
        InputError: if there are duplicate u id's for the input
        InputError: invalid id

    Returns:
        dictionary: contains dm_id
    """
    store = data_store.get()
    validate_token(token)
    auth_user_id = decode_token(token)['auth_user_id']

    if check_duplicate(list_of_u_ids):
        raise InputError("there are duplicate u id's")

    if check_invalid_id(store, list_of_u_ids):
        raise InputError

    if store == {}:
        new_dm_id = 1
    else:
        new_dm_id = len(store['channels']) + 1

    handle_list = []
    for ids in list_of_u_ids:
        for users in store['users']:
            if ids == users['u_id']:
                handle_list.append(users['handle_str'])

    handle_list.sort()
    new_name = ', '.join(handle_list)

    new_dm = {
        'dm_id': new_dm_id,
        'name': new_name,
        'owner_members': [auth_user_id],
        'all_members': list_of_u_ids,
        'messages_list': [],
        'start': 25,
        'end': 75,
    }
    store['dms'].append(new_dm)

    data_store.set(store)

    return {
        'dm_id': store['dms'][-1]['dm_id']
    }


def check_duplicate(u_id_list):
    ''' Check if given list of user ids contains any duplicates '''
    if len(u_id_list) == len(set(u_id_list)):
        return False
    else:
        return True


def check_invalid_id(store, u_ids):
    '''Checks if any u_id passed in as argument for dm_create does not exist'''
    invalid = True
    for ids in u_ids:
        for user in store['users']:
            if ids == user['u_id']:
                invalid = False
        if invalid == True:
            return True


def dm_list_v1(token):
    """given a user, the list of dms the user is a part of
        is returned

    Args:
        token (string): user

    Raises:
        None

    Returns:
        dms (dictionary): contains a list of dms user is a part of under the key 'dms'
    """
    store = data_store.get()
    validate_token(token)
    auth_user_id = decode_token(token)['auth_user_id']['auth_user_id']

    dm_list = []

    for dms in store['dms']:
        if any(auth_user_id in dms['owner_members'], auth_user_id in dms['all_memebers']):
            details_list = (extract_dm_details(store, dms['dm_id']))
            new = {
                "dm_id": details_list["dm_id"],
                "name": details_list["name"]
            }
            dm_list.append(new)

    data_store.set(store)

    return {
        'dms': dm_list
    }


def extract_dm_details(store, dm_id):
    '''given a dm_id, it returns the dictionary containing the details of the dm'''
    for dms in store['dms']:
        if dms['dm_id'] == dm_id:
            return dms


def dm_remove_v1(token, dm_id):
    """removes an existing dm so all members are
        no longer a part of the dm.
        this action can only be done by the owner of the dm

    Args:
        token (string): owner fo the dm
        dm_id (int): dm to be removed

    Raises:
        AccessError: the authorised user is not the original creator of the DM
        InputError: the dm_id provided is invalid
        AccessError: The authorised user is no longer a part of the DM

    Returns:
        dictionary: empty
    """
    store = data_store.get()
    validate_token(token)
    auth_user_id = decode_token(token)['auth_user_id']['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError

    if not is_dm_owner(store, auth_user_id, dm_id):
        raise AccessError

    if not is_dm_member(store, auth_user_id, dm_id):
        raise AccessError

    count = 0
    for dms in store['dms']:
        if dms['dm_id'] == dm_id:
            store['dms'].pop(count)
        count += 1

    data_store.set(store)

    return {

    }


def valid_dm_id(store, dm_id):
    '''returns True if a dm with the dm_id passed in argument exists in data_store'''
    dm_exist = False
    for dms in store['dms']:
        if dm_id == dms['dm_id']:
            dm_exist = True
    return dm_exist


def is_dm_owner(store, auth_user_id, dm_id):
    '''the user with the given auth_user_id is an owner of the dm with the given dm_id'''
    dm_owner = False
    for dms in store['dms']:
        if dms['dm_id'] == dm_id and auth_user_id in dms['owner_members']:
            dm_owner = True
    return dm_owner


def is_dm_member(store, auth_user_id, dm_id):
    dm_member = False
    for dms in store['dms']:
        if dms['dm_id'] == dm_id and auth_user_id in dms['all_members']:
            dm_member = True
    return dm_member


def dm_details_v1(token, dm_id):
    """provides basic details about a specific dm.
        details are name and members of dm

    Args:
        token (string): authorised user who is part of the dm
        dm_id (int): if of dm

    Raises:
        InputError: if the dm id does not exit
        AccessError: dm id exists but the user is not a part of the dm

    Returns:
        dictionary: contains the name and members of the dm
    """
    store = data_store.get()
    validate_token(token)
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError("dm does not exist")

    if not is_dm_member(store, u_id, dm_id):
        raise AccessError("user is not part of dm")

    for dm in store['dms']:
        if dm_id == dm["dm_id"]:
            name = dm["name"]
            members = dm["members"]

    data_store.set(store)

    return {
        "name": name,
        "members": members
    }


def dm_leave_v1(token, dm_id):
    """user leaves a certain dm.
        given dm ID the user is removed from DM
        a creator can be removed from a dm and it will still exist
        the name of the dm will remain the same

    Args:
        token (string): user who is leaving dm
        dm_id (int): dm user will be leaving

    Raises:
        InputError: if dm id does not exist
        AccessError: if user is not a part of the dm

    Returns:
        dictionary: empty
    """
    store = data_store.get()
    validate_token(token)
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError("dm id does nto exist")

    if not is_dm_member(store, u_id, dm_id):
        raise AccessError("user is not part of dm")

    for dm in store["dms"]:
        if dm_id == dm["dm_id"]:
            dm.remove(u_id)

    data_store.set(store)

    return {}


def dm_messages_v1(token, dm_id, start):
    """returns up to 50 messages in dm based on the start

    Args:
        token (string): authorised user
        dm_id (int): given dm
        start (int): requested start for messages

    Raises:
        InputError: dm id does not exist
        AccessError: user is not aprt of dm
        InputError: start value greater than messages in dm

    Returns:
        dictionary: contains messages which is a list
        of dictionary containing the messages id, message,
        user who made the message and time send. Also contains
        the start and end for the messages. End will be -1 if
        it returns less than 50 messages.
    """
    store = data_store.get()
    validate_token(token)
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError("dm id does not exist")

    if not is_dm_member(store, u_id, dm_id):
        raise AccessError("user is not part of dm")

    for dm in store["dms"]:
        if dm_id == dm["dm_id"]:
            if len(dm["messages"]) < start:
                raise InputError(
                    "start value gerater than messages in dm"
                )
            id_list = dm["messages_list"]

    ret = []
    st = start
    end = start + 50
    for m in reversed(store["messages"]):
        if st >= end:
            break
        if id_list[st] == m["message_id"]:
            ret_dict = {
                "message_id": m["message_id"],
                "u_id": m["u_id"],
                "message": m["message"],
                "time_sent": m["time_sent"]
            }
            ret.append(ret_dict)
            st += 1

    if st < end:
        st = -1

    data_store.set(store)

    return {
        "messages": ret,
        "start": start,
        "end": st
    }
