from base64 import decode
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
    store = data_store.get()
    auth_user_exist = False
    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

    if check_duplicate(u_ids):
        raise InputError

    if check_invalid_id(store, u_ids):
        raise InputError

    if store == {}:
        new_dm_id = 1
    else:
        new_dm_id = len(store['channels']) + 1

    handle_list = []
    for ids in u_ids:
        for users in store['users']:
            if ids == users['u_id']:
                handle_list.append(users['handle_str'])

    handle_list.sort()
    new_name = ', '.join(handle_list)


    new_dm = {
        'dm_id': new_dm_id,
        'name': new_name,
        'owner_members': [auth_user_id],
        'all_members': u_ids,
        'messages_list': [],
        'start': 25,
        'end': 75,
    }
    store['dms'].append(new_dm)

    return {
        'dm_id': store['dms'][-1]['dm_id']
    }

def check_duplicate(u_id_list):
    ''' Check if given list contains any duplicates '''
    if len(u_id_list) == len(set(u_id_list)):
        return False
    else:
        return True

def check_invalid_id(store, u_ids):
    invalid = True
    for ids in u_ids:
        for user in store['users']:
            if ids == user['u_id']:
                invalid = False
        if invalid == True:
            return True

def dm_list_v1(token):
    store = data_store.get()
    auth_user_exist = False
    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

    dm_list = []

    for dms in store['dms']:
        if any(auth_user_id in dms['owner_members'], auth_user_id in dms['all_memebers']):
            details_list = (extract_dm_details(store, dms['dm_id']))
            new = {
                "dm_id" : details_list["dm_id"],
                "name" : details_list["name"]
            }
            dm_list.append(new)

    return {
        'dms': dm_list
    }


def extract_dm_details(store, dm_id):
    for dms in store['dms']:
        if dms['dm_id'] == dm_id:
            return dms



def dm_remove_v1(token, dm_id):
    store = data_store.get()
    auth_user_exist = False
    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

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

    return {

    }

def valid_dm_id(store, dm_id):
    dm_exist = False
    for dms in store['dms']:
        if dm_id == dms['dm_id']:
            dm_exist = True
    return dm_exist

def is_dm_owner(store, auth_user_id, dm_id):
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
    store = data_store.get()
    validate_token(token)
    u_id = decode_token(token)

    if not valid_dm_id(store, dm_id):
        raise InputError

    if not is dm_member(store, u_id, dm_id):
        raise AccessError

    for dms in store['dms']:
        if dm_id == dm["dm_id"]:
            name = dm["name"]
            members = dm["members"]

    return {
        "name" : name,
        "members" : members
    }

#{ name, members }
