from base64 import decode
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper import decode_token, validate_token
"""Channels has the 3 functions: create, list, listall

Functions:
    channels_create: creates a channel
    channels_list: list the channels a certain user is a part of
    channels_listall: lists all the channels
"""


def channels_list_v1(token):
    """ Lists all the channels that only the given user is a part of
    either as a ownder or member

    Args:
        auth_user_id (u_id): A valid user that has been registered

    Raises:
        AccessError: the auth_user is not a registered user

    Returns:
        Dictionary containing list of dictionaries:
    """

    store = data_store.get()
    auth_user_exist = False
    auth_user_id = decode_token(token)['auth_user_id']

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

    for accounts in store['users']:
        if accounts['u_id'] == auth_user_id:
            output_list = create_list_dictionary(accounts)
    return {
        'channels': output_list
    }
    # {
    #     'channels': [
    #         {
    #             'channel_id': (channel id)
    #             'name': (channel name)
    #         }
    #     ]
    # }


def create_list_dictionary(accounts):
    """ Appends the list of dictionaries stored in the 'channels_owned'
    and 'channels_joined' dictionaries in the data store, representing all
    the channels the user is associated with.

    Args:
        Accounts: accounts is the account of that given user
    Raises:
        None

    Returns:
        List of dictionaries
    """

    output_list = []
    for owned in accounts['channels_owned']:
        channel = {
            'channel_id': owned['channel_id'],
            'name': owned['name']
        }
        output_list.append(channel)

    for joined in accounts['channels_joined']:
        channel = {
            'channel_id': joined['channel_id'],
            'name': joined['name']
        }
        output_list.append(channel)
    return output_list
    # [
    #     {
    #         'channel_id': (channel id),
    #         'name': (channel name)
    #     }
    # ]


def channels_listall_v1(token):
    """ Lists all the channels created, both private and public

    Args:
        auth_user_id (u_id): A valid user that has been registered

    Raises:
        AccessError: the auth_user is not a registered user

    Returns:
        Dictionary containing list of dictionaries:
    """

    store = data_store.get()
    store_channels = store['channels']
    auth_user_id = decode_token(token)['auth_user_id']
    auth_user_exist = False

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

    all_channels = []
    for channel in store_channels:
        channel_dict = {
            'channel_id': channel['channel_id'],
            'name': channel['name'],
        }
        all_channels.append(channel_dict)

    return {
        'channels': all_channels
    }
    # {
    #     'channels': [
    #         {
    #             'channel_id': (channel id)
    #             'name': (channel name)
    #         }
    #     ]
    # }


def channels_create_v1(token, name, is_public):
    """ Function to create a new channel given the correct user id of a authorised user,
    the name of the channel and whether or not the channel is public or private. The return
    of this function is the id of that channel

    Args:
        auth_user_id (u_id): A valid user that intends to create the channel
        name (channel_id): the desired name for the channel to be created
        is_public (boolean): either True for it its public or False if private

    Raises:
        AccessError: the auth_user is not a registered user

    Returns:
        Dictionary
    """

    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']
    auth_user_exist = False

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

    if len(name) > 20:
        raise InputError(
            "The name of the channel cannot be more than 20 characters.")

    if len(name) < 1:
        raise InputError(
            "The name of the channel cannot be less than 1 character.")

    if store == {}:
        new_channel_id = 1
    else:
        new_channel_id = len(store['channels']) + 1

    new_channel = {
        'channel_id': new_channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [auth_user_id],
        'all_members': [auth_user_id],
        'messages': [],
        'start': 0,  # ditto
        'end': 50,
    }

    for users in store['users']:
        if users['u_id'] == auth_user_id:
            users['channels_owned'].append(new_channel)

    store['channels'].append(new_channel)
    data_store.set(store)

    return {
        'channel_id': store['channels'][-1]['channel_id']
    }

    # {
    #     'channel_id': (channel id)
    # }
