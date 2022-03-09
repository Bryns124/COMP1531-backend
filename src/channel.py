from src.data_store import data_store
from src.error import AccessError, InputError

def channel_invite_v1(auth_user_id, channel_id, u_id):
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

    auth_user_exist = False
    user_exist = False

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True
        elif u_id == user['u_id']:
            user_exist = True

    if not auth_user_exist:
        raise AccessError

    if not user_exist:
        raise InputError

    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True

    if not channel_exist:
        raise InputError

    already_member = False
    can_invite = False
    for members in store['channels'][channel_id - 1]['all_members']:
        if members == u_id:
            already_member = True
        elif members == auth_user_id:
            can_invite = True

    if already_member:
        raise InputError

    if not can_invite:
        raise AccessError

    for channel in store['channels']:
        for user in store['users']:
            if u_id == user['u_id']:
                invited_member = user['u_id']
                user['channels_joined'].append(channel)
        if channel["channel_id"] == channel_id:
            channel['all_members'].append(invited_member)


    # print(store['channels'])

    data_store.set(store)
    return {
    }

def channel_details_v1(auth_user_id, channel_id):

    '''
    channel_details_v1(auth_user_id, channel_id)

    Given a channel with ID channel_id that the authorised user is a member of, provide
    basic details about the channel.

    returns a dictionary
    {
        "channel_name": name of the channel (string),
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

    store = data_store.get() # Accessing data_store for data

    is_channel = False # Initialising booleans for raising errors
    is_member = False
    is_valid_auth_user_id = False
    all_channels = store['channels'] # Saving list of channels as a local variable

    # Iterates over all users and checks if the provided user id is in the system
    for user in store['users']:
        if user['u_id'] == auth_user_id:
            is_valid_auth_user_id = True # if the user id is found the boolean for
            # valid user is set to True

    # if the user id is not in the system, raises an InputError
    if not is_valid_auth_user_id:
        raise AccessError("Invalid User ID")

    # Iterates over all the channels and check if the provided channel id is in
    # the system
    for channel in all_channels:
        if channel['channel_id'] == channel_id:
            is_channel = True # if the channel id is found the boolean for valid
            # channel is set to True
            active_channel = channel # sets the given channel as active channel
            # to use it later in the function

    # if the channel id is not in the system, raises an InputError
    if not is_channel:
        raise InputError("Invalid Channel ID")

    # Iterates over all members in the channel to check if the provided user id
    # is a member of the channel
    for member in active_channel['all_members']:
        if member == auth_user_id:
            is_member = True # if the user is found in the channel, the boolean
            # saving if the user is a channel member is set to True

    # if the user is not a member of the channel, raises an InputError
    if not is_member:
        raise AccessError()

    # initialising lists to save details about each owner/member respectively
    owner_members_details = []
    all_members_details = []

    # Iterates over every id in the list of owner members/all members
    # respectively
    for owner_id in active_channel['owner_members']:
        # saves a dictionary containing details about a owner in owner_current
        # and appends that to the list containing details
        # about every owner
        owner_current = member_details(owner_id)
        owner_members_details.append(owner_current)

    for member_id in active_channel['all_members']:
        # does the same as previous but for all members
        # saves a dictionary containing details about a member in member_current
        # and appends that to the list containing details
        # about every member
        member_current = member_details(member_id)
        all_members_details.append(member_current)

    # returns a dictionary with the format specified in the docstring for this
    # function
    return {
        'channel_name': active_channel['channel_name'],
        'is_public': active_channel['is_public'],
        'owner_members': owner_members_details,
        'all_members': all_members_details
    }

def member_details(user_id):
    '''
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
    store = data_store.get() # retrieves data from data_store
    users = store['users'] # saves list of dictionaries containing information
    # about all users

    # iterates over all users and finds the user that matches the provided
    # user_id
    for user in users:
        if user['u_id'] == user_id:
            # returns the required information in a dictionary specified in
            # the docstring
            return {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str']
            }
    # returns None if user is not found,
    return

def channel_messages_v1(auth_user_id, channel_id, start):
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

    auth_user_exist = False

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError

    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True

    if not channel_exist:
        raise InputError

    if len(store['channels'][channel_id - 1]['messages']) < start:
        raise InputError

    in_channel = False

    for members in store['channels'][channel_id -1]['all_members']:
        if members == auth_user_id:
                in_channel = True

    if not in_channel:
        raise AccessError
    returned_messages = {'messages' : [], 'start': start, 'end': ""}
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

    return  returned_messages
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



def channel_join_v1(auth_user_id, channel_id):
    '''
    function allows user to join another channel based on the channel ID
    will give input error if the channel id is invalid or if the user is already in the channel
    will give access error if the channel ID is one for a private channel
    '''
    store = data_store.get()

    auth_user_exist = False

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise InputError

    if not channel_validity(channel_id, store):
        raise InputError("Channel id is invalid.")

    if already_member(auth_user_id, channel_id, store):
        raise InputError("The user is already a member of this channel.")

    current_channel = extract_channel_details(channel_id, store)
    if not current_channel['is_public']:
        raise AccessError("This is a private channel, user does not have access.")


    for user_accounts in store['users']:
        if user_accounts['u_id'] == auth_user_id:
            new_member = user_accounts['u_id']
            user_accounts['channels_joined'].append(current_channel)

    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channels['all_members'].append(new_member)

    data_store.set(store)
    return


def channel_validity(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            return True
    return False


def already_member(auth_user_id, channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id in channels['all_members'] or auth_user_id in channels['owner_members']:
                return True
    return False


def extract_channel_details(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channel_details = channels
    return channel_details


