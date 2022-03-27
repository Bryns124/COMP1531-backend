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


def dm_create_v1(token, u_ids):
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
    auth_user_id = decode_token(token)['auth_user_id']

    if check_duplicate(auth_user_id, u_ids):
        raise InputError(description="there are duplicate u id's")

    if check_invalid_id(store, u_ids):
        raise InputError(description="There is a invalid u_id")

    if store["dms"] == []:
        new_dm_id = 1
    else:
        new_dm_id = len(store['dms']) + 1

    handle_list = []

    for user in store['users']:
        if user["u_id"] == auth_user_id:
            handle_list.append(user["handle_str"])

    for ids in u_ids:
        for users in store['users']:
            if ids == users['u_id']:
                handle_list.append(users['handle_str'])

    handle_list.sort()
    new_name = ', '.join(handle_list)

    new_dm = {
        "dm_id": new_dm_id,
        'name': new_name,
        'owner_members': [auth_user_id],
        'all_members': u_ids,
        'messages_list': [],
        'start': 25,
        'end': 75,
    }
    store['dms'].append(new_dm)

    data_store.set(store)

    return {
        "dm_id": new_dm["dm_id"]
    }


def check_duplicate(auth_user_id, u_id_list):
    ''' Check if given list of user ids contains any duplicates '''
    if len(u_id_list) == len(set(u_id_list)) and auth_user_id not in u_id_list:
        return False
    else:
        return True


def check_invalid_id(store, u_ids):
    '''Checks if any u_id passed in as argument for dm_create does not exist'''
    for ids in u_ids:
        invalid = True
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
    auth_user_id = decode_token(token)['auth_user_id']
    dm_list = []

    for dm in store["dms"]:
        if auth_user_id in dm["owner_members"] or auth_user_id in dm['all_members']:
            new = {
                "dm_id": dm["dm_id"],
                "name": dm["name"]
            }
            dm_list.append(new)

    data_store.set(store)

    return {
        'dms': dm_list
    }


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
    auth_user_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does not exist")

    if not is_dm_owner(store, auth_user_id, dm_id):
        raise AccessError(description="user is not owner of dm")

    i = 0
    while i < len(store["dms"]):
        if store["dms"][i]["dm_id"] == dm_id:
            del store["dms"][i]
            break
        i += 1

    data_store.set(store)

    return {

    }


def valid_dm_id(store, dm_id):
    '''returns True if a dm with the dm_id passed in argument exists in data_store'''
    for dms in store['dms']:
        if dm_id == dms["dm_id"]:
            return True
    return False


def is_dm_owner(store, auth_user_id, dm_id):
    '''the user with the given auth_user_id is an owner of the dm with the given dm_id'''
    for dms in store['dms']:
        if dms["dm_id"] == dm_id and auth_user_id in dms['owner_members']:
            return True
    return False


def is_dm_member(store, auth_user_id, dm_id):
    for dms in store['dms']:
        if dms["dm_id"] == dm_id and auth_user_id in dms['all_members']:
            return True
    return False


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
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm does not exist")

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")

    for dm in store['dms']:
        if dm_id == dm["dm_id"]:
            name = dm["name"]
            members = dm["owner_members"] + dm["all_members"]

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
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does nto exist")

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")

    for dm in store["dms"]:
        if dm_id == dm["dm_id"]:
            if is_dm_member(store, u_id, dm_id):
                dm["all_members"].remove(u_id)
            else:
                dm["owner_members"].remove(u_id)

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
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does not exist")

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")

    for dm in store["dms"]:
        if dm_id == dm["dm_id"]:
            curr_dm = dm

    if len(curr_dm["messages_list"]) < start:
        raise InputError("start value gerater than messaegs in dm")

    # for m in reversed(store["messages"]):
    #     if end == -1 and curr >= len(messages_list):
    #         break
    #     if end == start + 50 or curr >= end - 1:
    #         break
    #     if messages_list[curr] == m["message_id"]:
    #         ret_dict = {
    #             "message_id": m["message_id"],
    #             "u_id": m["u_id"],
    #             "message": m["message"],
    #             "time_sent": m["time_sent"]
    #         }
    #         ret.append(ret_dict)
    #         curr += 1

    if 50 > len(curr_dm["messages_list"]):
        end = -1
    elif 50 <= len(curr_dm["messages_list"]):
        end = start + 50

    ret = []
    counter = 0
    for id in curr_dm["messages_list"]:
        if counter >= 50:
            break
        for m in store["messages"]:
            if id == m["message_id"]:
                ret_dict = {
                    "message_id": m["message_id"],
                    "u_id": m["u_id"],
                    "message": m["message"],
                    "time_sent": m["time_sent"]
                }
                ret.append(ret_dict)
        counter += 1
    # data_store.set(store)
    return {
        "messages": ret,
        "start": start,
        "end": end
    }
