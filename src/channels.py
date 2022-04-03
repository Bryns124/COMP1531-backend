from base64 import decode
from src.data_store import data_store, User, Channel
from src.error import InputError, AccessError
from src.helper import decode_token, validate_token
# from src.userclass import User
# from src.channeldmclass import Channel
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
    auth_user_id = decode_token(token)['auth_user_id']
    owned_dict = store["users"][auth_user_id].channels_owned
    joined_dict = store["users"][auth_user_id].channels_joined

    output = []

    for owned in owned_dict:
        new_owned = {
            "channel_id": owned,
            "name": owned_dict[owned].name
        }
        output.append(new_owned)

    for joined in joined_dict:
        new_joined = {
            "channel_id": joined,
            "name": joined_dict[joined].name
        }
        output.append(new_joined)

    return {
        'channels': output
    }


def channels_listall_v1(token):
    """ Lists all the channels created, both private and public

    Args:
        auth_user_id (u_id): A valid user that has been registered

    Raises:
        AccessError: the auth_user is not a registered user

    Returns:
        Dictionary containing list of dictionaries:
    """

    decode_token(token)['auth_user_id']
    channels = data_store.get()["channels"]

    all_channels = []
    for channel in channels:
        channel_dict = {
            "channel_id": channel,
            "name": channels[channel].name
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

    if len(name) > 20:
        raise InputError(
            description="The name of the channel cannot be more than 20 characters.")

    if len(name) < 1:
        raise InputError(
            description="The name of the channel cannot be less than 1 character.")

    new_channel = Channel(auth_user_id, name, is_public)
    store = data_store.get()
    store["channels"][new_channel.channel_id] = new_channel
    store["users"][auth_user_id].add_ch_owned(
        new_channel.channel_id, new_channel)
    new_channel.add_owner(auth_user_id)
    data_store.set(store)

    return {
        'channel_id': new_channel.channel_id
    }
