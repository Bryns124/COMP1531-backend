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
    dm_messages: returns upto 50 messsages of the DM associated with the provided DM_id
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
    new_dm_name = ', '.join(handle_list)


    new_dm = {
        'DM_id': new_dm_id,
        'DM_name': new_dm_name,
        'owner_members': [auth_user_id],
        'all_members': u_ids,
        'messages_list': [],
        'start': 25,
        'end': 75,
    }
    store['DM'].append(new_dm)

    return {
        'DM_id': store['DM'][-1]['DM_id']
    }


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

    for dms in store['DM']:
        if any(auth_user_id in dms['owner_members'], auth_user_id in dms['all_memebers']):
            dm_list.append(extract_dm_details(store, dms['DM_id']))


    def extract_dm_details(store, dm_id):
        for dms in store['DM']:
            if dms['DM_id'] == dm_id:
                return dms