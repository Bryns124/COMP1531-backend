from base64 import decode
from json import load
from src.data_store import data_store
from src.error import AccessError, InputError
from src.helper import decode_token, generate_token, validate_token, already_member, channel_validity, user_validity, valid_auth_user_id, extract_channel_details, load_channel, load_message, load_user, notify_add
from src.classes import User, Channel

"""
Channel contains the functionality which allows for the inviting of users, calling the
details of channels, calling messages and joining channels. ß

    channel_invite_v1: allows a user to invite another user to a channel.
    channel_details_v1: provides the details of a channel.
    channel_messages_v1: returns all the messages within a channel.
    channel_join_v1: allows a user to join a channel.
    channel_leave_v1: allows a user to leave a channel.

"""


def channel_invite_v1(token, channel_id, u_id):
    """
    Allows a authorized user to invite another user to a channel they are apart of.

    Args:
        token (string): The token of the user who is apart of the channel.
        channel_id (channel_id): The channel id auth_user is inviting to.
        u_id (u_id): A valid second user who is being invited.

    Raises:
        InputError: u_id dos not exist in datastore.
        InputError: channel_id does not exist in datastore.
        InputError: the invited user is already part of the channel.
        AccessError: the auth_user is not in the channel they are inviting to.

    Returns:
        dictionary: nothing! nothing is returned after a invite
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']
    load_user(u_id)
    if not channel_validity(channel_id, store):
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    if already_member(u_id, channel_id, store):
        raise InputError(
            description="The member you are trying to invite is already apart of the channel.")

    if not already_member(auth_user_id, channel_id, store):
        raise AccessError(
            description="You are not apart of the channel you are trying to invite to.")

    ch_object = store["channels"][channel_id]
    store["users"][u_id].add_channel(channel_id, ch_object)
    ch_object.add_member(u_id, store["users"][u_id])
    notify_add(u_id, store["users"][auth_user_id].handle,
               channel_id, ch_object.name, True)
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
    """

    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not channel_validity(channel_id, store):
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    if not already_member(auth_user_id, channel_id, store):
        raise AccessError(description="You are not a member of the channel.")

    owner_members_details = []
    all_members_details = []

    owner_dict = store["channels"][channel_id].owner_members
    member_dict = store["channels"][channel_id].all_members

    for owner in owner_dict:
        owner_current = user_details(owner_dict[owner])
        owner_members_details.append(owner_current)

    for member in member_dict:
        member_current = user_details(member_dict[member])
        all_members_details.append(member_current)

    channel = store["channels"][channel_id]
    return {
        'name': channel.name,
        'is_public': channel.is_public,
        'owner_members': owner_members_details,
        'all_members': all_members_details

    }


def user_details(user_object):
    """
    user_details(user_id)

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
    """

    return {
        'u_id': user_object.auth_user_id,
        'email': user_object.email,
        'name_first': user_object.name_first,
        'name_last': user_object.name_last,
        'handle_str': user_object.handle
    }


def channel_messages_v1(token, channel_id, start):
    """
    Taking a valid user it pulls a list of up to 50 messages from a starting
    point and returns them.
    Args:
        token (string): The token of the user calling the messages.
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

    decode_token(token)['auth_user_id']

    if channel_id not in store["channels"]:
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    active_channel = store["channels"][channel_id]
    if len(active_channel.message_list) < start:
        raise InputError(
            description="Your start value is greater than the messages in the channel.")

    try:
        active_channel.all_members[decode_token(token)['auth_user_id']]
    except:
        raise AccessError(
            description="You are not part of that channel.") from AccessError

    returned_messages = {'messages': [], 'start': start, 'end': ""}
    returned_full = False
    number_of_messages = 0
    for message_id in list(reversed(list(active_channel.message_list)))[start: start + 50]:
        returned_messages['messages'].append(
            {'message_id': store['messages'][message_id].id,
             'u_id': store['messages'][message_id].u_id,
             'message': store['messages'][message_id].message,
             'time_sent': store['messages'][message_id].time_sent})
        number_of_messages += 1

        if number_of_messages == 50:
            returned_full = True

    if returned_full:
        returned_messages['end'] = (start + 50)
    else:
        returned_messages['end'] = -1

    return returned_messages


def channel_join_v1(token, channel_id):
    """
    function allows user to join another channel based on the channel ID
    will give input error if the channel id is invalid or if the user is already in the channel
    will give access error if the channel ID is one for a private channel
    """
    store = data_store.get()

    auth_user_id = decode_token(token)['auth_user_id']

    if not channel_validity(channel_id, store):
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    if already_member(auth_user_id, channel_id, store):
        raise InputError(description="You are aleady a member of this channel")

    if not store["channels"][channel_id].is_public:
        raise AccessError(
            description="This is a private channel, user does not have access.")

    ch_object = store["channels"][channel_id]
    store["users"][auth_user_id].add_channel(channel_id, ch_object)
    ch_object.add_member(auth_user_id, store["users"][auth_user_id])
    data_store.set(store)
    return {}


def channel_leave_v1(token, channel_id):
    """
    Takes user and removes them from the channel's list of users and owners, if they are an owner
    Fails if channel_id is invalid (InputError)
    Fails if user does not exist or is not a part of the channel (AccessError)
    """
    auth_user_id = decode_token(token)["auth_user_id"]

    store = data_store.get()
    if not channel_validity(channel_id, store):
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    if not already_member(auth_user_id, channel_id, store):
        raise AccessError(
            description="You are aleady a member of this channel")
    # TO PUT LATER: user is start of active standup

    store["channels"][channel_id].user_leave(auth_user_id)
    store["users"][auth_user_id].channel_leave(channel_id)
    data_store.set(store)
    return {}


def channel_addowner_v1(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of the channel.
    Args:
        token: the user's token
        channel_id: the channel's channel_id
        u_id: the channel's u_id
    Return:
        Nothing
    Raises:
        InputError: channel_id does not refer to a valid channel
        InputError: u_id does not refer to a valid user
        InputError: u_id refers to a user who is not a member of the channel
        InputError: u_id refers to a user who is already an owner of the channel
        AccessError: channel_id is valid and the authorised user does not have owner permissions in the channel
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not channel_validity(channel_id, store):
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    load_user(u_id)

    if auth_user_id not in store["channels"][channel_id].owner_members:
        raise AccessError(
            description="Authorised user does not have owner permissions in channel.")

    if not already_member(u_id, channel_id, store):
        raise InputError(
            description="User to be made owner is not a member of channel")

    if u_id in store["channels"][channel_id].owner_members:
        raise InputError(
            description="This user is already an owner of the channel")

    store["channels"][channel_id].add_owner(u_id, store["users"][u_id])
    store["users"][u_id].add_ch_owned(
        channel_id, store["channels"][channel_id])
    data_store.set(store)
    return {}


def channel_removeowner_v1(token, channel_id, u_id):
    """
    Make user with user id u_id an owner of the channel.
    Args:
        token: the user's token
        channel_id: the channel's channel_id
        u_id: the channel's u_id
    Return:
        Nothing
    Raises:
        InputError: channel_id does not refer to a valid channel
        InputError: u_id does not refer to a valid user
        InputError: u_id refers to a user who is not an owner of the channel
        InputError: u_id refers to a user who is currently the only owner of the channel
        AccessError: channel_id is valid and the authorised user does not have owner permissions in the channel
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not channel_validity(channel_id, store):
        raise InputError(
            description="The input channel_id does not exist in the datastore.")

    load_user(u_id)

    if auth_user_id not in store["channels"][channel_id].owner_members:
        raise AccessError(
            description="Authorised user does not have owner permissions in channel.")

    if u_id not in store["channels"][channel_id].owner_members:
        raise InputError(
            description="This user is not and owner and so can't be removed")

    if len(store["channels"][channel_id].owner_members) == 1:
        raise InputError(
            description="You are the only owner and cannot remove youself")

    store["channels"][channel_id].remove_owner(u_id)
    store["users"][u_id].remove_ch_owned(channel_id)
    data_store.set(store)
    return {}
