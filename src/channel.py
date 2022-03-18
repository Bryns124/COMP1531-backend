from base64 import decode
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper import decode_token, generate_token, validate_token, already_member, channel_validity, valid_auth_user_id, extract_channel_details
"""
Channel contains the functionality which allows for the inviting of users, calling the
details of channels, calling messages and joining channels. ß
"""


def channel_invite_v1(token, channel_id, u_id):
    """
    Allows a authorized user to invite another user to a channel they are apart of.

    Args:
        auth_user_id (u_id): A valid user who is apart of the channel/
        channel_id (channel_id): The channel id auth_user is inviting to.
        u_id (u_id): A valid second user who is being invited

    Raises:
        InputError: u_id dos not exist in datastore.
        InputError: channel_id does not exist in datastore.
        InputError: the invited user is already part of the channel.
        AccessError: the auth_user is not in the channel they are inviting to.

    Returns:
        dictionary: nothing! nothing is returned after a invite
    """
    store = data_store.get()

    user_exist = False
    auth_user_id = decode_token(token)['auth_user_id']
    valid_auth_user_id(auth_user_id)
    for user in store['users']:
        if u_id == user['u_id']:
            user_exist = True

    if not user_exist:
        raise InputError("The input u_id does not exist in the datastore.")

    if not channel_validity(channel_id, store):
        raise InputError(
            "The input channel_id does not exist in the datastore.")

    if already_member(u_id, channel_id, store):
        raise InputError(
            "The member you are trying to invite is already apart of the channel.")

    if not already_member(auth_user_id, channel_id, store):
        raise AccessError(
            "You are not apart of the channel you are trying to invite to.")

    for channel in store['channels']:
        for user in store['users']:
            if u_id == user['u_id']:
                invited_member = user['u_id']
                user['channels_joined'].append(channel)
        if channel["channel_id"] == channel_id:
            channel['all_members'].append(invited_member)
    data_store.set(store)
    return {
    }


def channel_details_v1(token, channel_id):
    """
    channel_details_v1(token, channel_id)

    Given a channel with ID channel_id that the authorised user is a member of, provide
    basic details about the channel.

    returns a dictionary
    {
        "name": name of the channel (string),
        "is_public": whether or not the channel is public (boolean),
        "owner_members": a list of dictionaries containing owner users, each
        dictionary being of the form:
        {
        "u_id": user id (string),
        "email": email (string),
        "name_first": first name (string),
        "name_last": last name (string),
        "handle_str": user handle (string)
        }
        "all_members": a list of dictionaries in the same format as owner_members,
        however containing information
        on all members of the channel
    }
    '''

    store = data_store.get()

    is_channel = False 
    is_member = False
    all_channels = store['channels'] 

    valid_auth_user_id(auth_user_id)
    
    for channel in all_channels:
        if channel['channel_id'] == channel_id:
            is_channel = True 
            active_channel = channel # sets the given channel as active channel
            # to use it later in the function

    if not is_channel:
        raise InputError("Invalid Channel ID")

    for member in active_channel['all_members']:
        if member == auth_user_id:
            is_member = True 
    
    if not is_member:
        raise AccessError("You are not a member of the channel.")

    owner_members_details = []
    all_members_details = []

    for owner_id in active_channel['owner_members']:
        owner_current = member_details(owner_id)
        owner_members_details.append(owner_current)

    for member_id in active_channel['all_members']:
        member_current = member_details(member_id)
        all_members_details.append(member_current)

    return {
        # 'name': 'Hayden',
        # 'owner_members': [
        #     {
        #         'u_id': 1,
        #         'email': 'example@gmail.com',
        #         'name_first': 'Hayden',
        #         'name_last': 'Jacobs',
        #         'handle_str': 'haydenjacobs',
        #     }
        # ],
        # 'all_members': [
        #     {
        #         'u_id': 1,
        #         'email': 'example@gmail.com',
        #         'name_first': 'Hayden',
        #         'name_last': 'Jacobs',
        #         'handle_str': 'haydenjacobs',
        #     }
        # ],
        'name': active_channel['name'],
        'is_public': active_channel['is_public'],
        'owner_members': owner_members_details,
        'all_members': all_members_details

    }


def member_details(user_id):
    """
    member_details(user_id)

    Given a user_id in data_store returns a dictionary containing details
    regarding that user.
    Returns None if user is not in data_store.

    returns a dictionary of the form:
    {
    "u_id": user id (string),
    "email": email (string),
    "name_first": first name (string),
    "name_last": last name (string),
    "handle_str": user handle (string)
    }

    '''
    store = data_store.get() 
    users = store['users'] 
    for user in users:
        if user['u_id'] == user_id:
            return {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str']
            }
    # returns None if user is not found,
    return {'name', 'is_public', 'owner_members', "all_members"}


def channel_messages_v1(token, channel_id, start):
    """_summary_
    Taking a valid user it pulls a list of up to 50 messages from a starting
    point and returns them.
    Args:
        auth_user_id (_u_id): The valid id of the user calling the messages.
        channel_id (channel_id): The channel_id of the channel which to call the
        messages from.
        start (int): A starting index value.

    Raises:
        InputError: u_id does not exist in data store.
        InputError: channel_id does not exist in data store.
        InputError: the starting index is greater than the messages in the
        channel.
        AccessError: u_id does not have access to the channel

    Returns:
        _type_: _description_
    """
    store = data_store.get()

    # print(store)
    validate_token(token)

    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True

    if not channel_exist:
        raise InputError(
            "The input channel_id does not exist in the datastore.")

    if len(store['channels'][channel_id - 1]['messages']) < start:
        raise InputError(
            "Your start value is greater than the messages in the channel.")

    in_channel = False

    for members in store['channels'][channel_id - 1]['all_members']:
        # do i need to contunue using tokens or do i need to extract auth_user_id
        if members == decode_token(token)['auth_user_id']:
            in_channel = True

    if not in_channel:
        raise AccessError("You are not part of that channel.")
    returned_messages = {'messages': [], 'start': start, 'end': ""}
    returned_full = False
    for messages in store['channels'][channel_id - 1]['messages']:
        if messages['message_id'] >= start & messages['message_id'] < (start + 50):
            returned_messages['messages'].append(messages)
        elif messages['message_id'] == (start + 50):
            returned_full = True

    if returned_full:
        returned_messages['end'] = (start + 50)
    else:
        returned_messages['end'] = -1
    # print(returned_messages)

    return returned_messages
    # {
    #     'messages': [
    #         {
    #             'message_id': 1,
    #             'u_id': 1,
    #             'message': 'Hello world',
    #             'time_created': 1582426789,
    #         }
    #     ],
    #     'start': 0,
    #     'end': 50,
    # }


def channel_join_v1(token, channel_id):
    """
    function allows user to join another channel based on the channel ID
    will give input error if the channel id is invalid or if the user is already in the channel
    will give access error if the channel ID is one for a private channel
    """
    store = data_store.get()

    valid_auth_user_id(decode_token(token)['auth_user_id'])

    if not channel_validity(channel_id, store):
        raise InputError("Channel id is invalid.")

    if already_member(decode_token(token)['auth_user_id'], channel_id, store):
        raise InputError("The user is already a member of this channel.")

    current_channel = extract_channel_details(channel_id, store)
    if not current_channel['is_public']:
        raise AccessError(
            "This is a private channel, user does not have access.")

    for user_accounts in store['users']:
        if user_accounts['u_id'] == decode_token(token)['auth_user_id']:
            new_member = user_accounts['u_id']
            user_accounts['channels_joined'].append(current_channel)

    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channels['all_members'].append(new_member)

    data_store.set(store)
    return {
        # empty
    }
