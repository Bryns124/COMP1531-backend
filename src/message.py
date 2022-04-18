from src.data_store import data_store
from src.helper import decode_token, detect_tagged_user, notify_react, validate_token, channel_validity, already_member, generate_timestamp, get_reacts
from src.error import AccessError, InputError
from src.classes import Message
from datetime import timezone
import datetime
from src.dm import valid_dm_id, is_dm_member, is_dm_owner
import threading


def messages_send_v1(token, channel_id, message):
    """_summary_
    Sends a message in specified channel.
    Args:
        token (string): The token of the user who is sending the message.
        channel_id (int): The channel which the message is being sent in.
        message (string): Message of user.

    Raises:
        InputError: Raised when the input channel is not valid
        AccessError: Raised when the user is not apart of the channel they are trying to msg in.

    Returns:
        int: Id of the message which was sent.
    """
    validate_message(message)
    new_message = do_messages_send_v1(token, channel_id, message)
    return {"message_id": new_message.id}


def do_messages_send_v1(token, channel_id, message):
    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']
    if not channel_validity(channel_id, store):
        raise InputError(description="The channel you have entered is invalid")
    if not already_member(u_id, channel_id, store):
        raise AccessError(description="User is not a member of the channel")

    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']

    parent = store['channels'][channel_id]

    new_message = Message(u_id, message, generate_timestamp(),
                          parent)
    store['users'][u_id].add_msg(new_message.id, new_message)
    store['channels'][channel_id].message_list.append(new_message.id)
    store['messages'][new_message.id] = new_message

    for user in detect_tagged_user(message, parent.all_members):
        notify_tagged_user(
            user, store['users'][u_id].handle, message, channel_id, parent.name, True)

    data_store.set(store)
    return new_message

def message_senddm_v1(token, dm_id, message):
    validate_message(message)
    new_dm_message = do_message_senddm_v1(token, dm_id, message)
    return {"message_id": new_dm_message.id}

def do_message_senddm_v1(token, dm_id, message):
    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does not exist")

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")

    new_dm_message = Message(
        u_id, message, generate_timestamp(), store['dms'][dm_id])
    store['dms'][dm_id].message_list.append(new_dm_message.id)
    store['messages'][new_dm_message.id] = new_dm_message
    store["users"][u_id].add_msg(new_dm_message.id, new_dm_message)

    for user in detect_tagged_user(message, store['dms'][dm_id].all_members):
        notify_tagged_user(
            user, store['users'][u_id].handle, message, dm_id, store['dms'][dm_id].name, False)

    data_store.set(store)
    return new_dm_message

def message_edit_v1(token, message_id, message):
    """edits a message based on the message id

    Args:
        token (string): user's token
        channel_id (int): channel id of where the message will be sent
        message (string): contains the message

    Raises:
        InputError: message exceeds 1000 characters
        InputError: message ID is not valid
        AccessError: user it not owner or user did not send message

    Returns:
        dictionary: empty dictionary
    """
    u_id = decode_token(token)['auth_user_id']
    validate_message(message)
    store = data_store.get()

    validate_mid(store["messages"], message_id)
    message_access(store, message_id, u_id)

    store['messages'][message_id].message = message

    data_store.set(store)
    return {}


def message_remove_v1(token, message_id):
    """rempves a message based on the message id

    Args:
        token (string): user's token
        channel_id (int): channel id of where the message will be sent
        message (string): contains the message

    Raises:
        InputError: message exceeds 1000 characters
        InputError: message ID is not valid
        AccessError: user it not owner or user did not send message

    Returns:
        dictionary: empty dictionary
    """
    u_id = decode_token(token)['auth_user_id']
    store = data_store.get()

    validate_mid(store["messages"], message_id)
    message_access(store, message_id, u_id)

    message = store['messages'][message_id]

    if message.parent.get_type() == "channel":
        message.parent.message_list.remove(message_id)
    elif message.parent.get_type() == "dm":
        message.parent.message_list.remove(message_id)

    data_store.set(store)
    return {}


def search_v1(token, query_str):

    """given query string, returns a collection of messages with that query

    Args:
        token (string): user's token
        query_str (string): message being searched

    Returns:
        messages: List of dictionaries, where each dictionary contains types
        { message_id, u_id, message, time_sent, reacts, is_pinned  }
    """
    auth_user_id = decode_token(token)['auth_user_id']
    validate_message(query_str)

    message_list = []
    messages = data_store.get()["messages"]
    for m in messages:
        if query_str in messages[m].message:
            new = {
                "message_id": messages[m].id,
                "u_id": messages[m].u_id,
                "message": messages[m].message,
                "time_sent": messages[m].time_sent,
                "reacts": get_reacts(m, auth_user_id),
                "is_pinned": messages[m].is_pinned
            }
            message_list.append(new)

    return {
        "messages": message_list
    }


def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """shares a message to either a specified dm or channel

    Args:
        token (string): user's token
        og_message_id (int): id of message to be shared
        message (string): additional message when sharing message
        channel_id (int): -1 if being shared to a dm
        dm_id (int): -1 if being shared to a channel

    Raises:
        InputError: both channel and dm id do not exist
        InputError: none of channel or dm id are -1
        InputError: both channel and dm id are -1
        InputError: message does not exist
        InputError: message (aditional message) is too long

    Returns:
        shared_message_id(int): treated like a "new" message id
    """
    store = data_store.get()

    if channel_id not in store["channels"] and dm_id not in store["dms"]:
        raise InputError("both channel and dm id are invalid")
    if channel_id != -1 and dm_id != -1:
        raise InputError("neither channel nor dm id are -1")
    if len(message) > 1000:
        raise InputError("additional message is too long")
    if og_message_id not in store["messages"]:
        raise InputError("This message does not exist")

    new_message = message + " " + store["messages"][og_message_id].message
    if message == "":
        new_message = store["messages"][og_message_id].message

    if dm_id == -1:
        new = do_messages_send_v1(token, channel_id, new_message)

    if channel_id == -1:
        new = do_message_senddm_v1(token, dm_id, new_message)

    data_store.set(store)
    return {
        "shared_message_id": new.id
    }


def message_sendlater_v1(token, channel_id, message, time_sent):
    """sends message to channel are specified time

    Args:
        token (string): user's token
        channel_id (int): channel sent to
        message (string): message beings sent
        time_sent (unix time stamp): future time to be sent at

    Raises:
        InputError: time is in the past
        InputError: channel is ivalid
        AccessError: user is not part of channel being sent to

    Returns:
        message_id: new message id
    """
    store = data_store.get()
    validate_message(message)
    u_id = decode_token(token)["auth_user_id"]
    if time_sent < generate_timestamp():
        raise InputError("Time is in the past")

    if not channel_validity(channel_id, store):
        raise InputError(description="The channel you have entered is invalid")
    if not already_member(u_id, channel_id, store):
        raise AccessError(description="User is not a member of the channel")

    delay = (time_sent - generate_timestamp())

    return threading.Timer(
        delay, messages_send_v1, (token, channel_id, message)
    ).start()



def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    """sends message to d, are specified time

    Args:
        token (string): user's token
        dm_id (int): dm sent to
        message (string): message beings sent
        time_sent (unix time stamp): future time to be sent at

    Raises:
        InputError: time is in the past
        InputError: dm is ivalid
        AccessError: user is not part of dm being sent to

    Returns:
        message_id: new message id
    """
    store = data_store.get()
    validate_message(message)
    u_id = decode_token(token)["auth_user_id"]
    if time_sent < generate_timestamp():
        raise InputError("Time is in the past")

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does not exist")

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")
    delay = (time_sent - generate_timestamp())

    return threading.Timer(
        delay, message_senddm_v1, (token, dm_id, message)
    ).start()



def message_dm_v1(token, dm_id, message, time_sent):
    store = data_store.get()
    validate_message(message)
    u_id = decode_token(token)["auth_user_id"]
    if time_sent < generate_timestamp():
        raise InputError("Time is in the past")

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does not exist")

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")
    delay = (time_sent - generate_timestamp())

    return threading.Timer(
        delay, message_senddm_v1, (token, dm_id, message)
    ).start()


def check_message_exists(message, auth_user_id):
    store = data_store.get()
    for m in store["messages"]:
        if store["messages"][m].message == message and auth_user_id in store["messages"][m].parent.all_members:
            return True
    raise InputError("message is not a valid message you are a part of")


def message_react_v1(token, message_id, react_id):
    """reacts to particular message

    Args:
        token (string): user's token
        message_id (int): message to be reacted
        react_id (int): reaction type

    Raises:
        InputError: react id is not a valid reaction
        InputError: message has already been reacted to

    Returns:
        empty dictionary
    """
    u_id = decode_token(token)['auth_user_id']
    store = data_store.get()

    validate_mid(store["messages"], message_id)
    message = store["messages"][message_id]

    if react_id <= 0:
        raise InputError(description='React ID is invalid')

    if message.is_user_reacted(u_id):
        raise InputError(
            description='You have already reacted to this message')

    message.react(u_id)

    author_id = store["messages"][message_id].u_id

    if message.parent.get_type() == "channel":
        notify_react(author_id, store["users"][u_id].handle, message.parent.id, message.parent.name, True)
    elif message.parent.get_type() == "dm":
        notify_react(author_id, store["users"][u_id].handle, message.parent.id, message.parent.name, False)

    data_store.set(store)
    return {}



def message_unreact_v1(token, message_id, react_id):
    """unreacts to particular message

    Args:
        token (string): user's token
        message_id (int): message to be unreacted
        react_id (int): reaction type

    Raises:
        InputError: react ID does not refer to a valid reaction type
        InputError: message is already unreacted

    Returns:
        empty dictionary
    """
    u_id = decode_token(token)['auth_user_id']
    store = data_store.get()

    validate_mid(store["messages"], message_id)

    if react_id <= 0:
        raise InputError(description='React ID is invalid')

    if not store["messages"][message_id].is_user_reacted(u_id):
        raise InputError(
            description='You have already unreacted to this message')

    store["messages"][message_id].unreact(u_id)

    return {}



def message_unreact_v1(token, message_id, react_id):
    """unreacts to particular message

    Args:
        token (string): user's token
        message_id (int): message to be unreacted
        react_id (int): reaction type

    Raises:
        InputError: react ID does not refer to a valid reaction type
        InputError: message is already unreacted

    Returns:
        empty dictionary
    """
    u_id = decode_token(token)['auth_user_id']
    store = data_store.get()

    validate_mid(store["messages"], message_id)

    if react_id <= 0:
        raise InputError(description='React ID is invalid')

    if not store["messages"][message_id].is_user_reacted(u_id):
        raise InputError(
            description='You have already unreacted to this message')

    store["messages"][message_id].unreact(u_id)
    data_store.set(store)


    return {}


def message_pin_v1(token, message_id):
    """given message is marked as pinned

    Args:
        token (string): user's token
        message_id (int): message to be pinned

    Raises:
        InputError: message doe snot exist
        InputError: user has not access to that message
        AccessError: user has no permission to pin message
        InputError: message is already pinned

    Returns:
        empty dictionary
    """

    auth_user_id = decode_token(token)["auth_user_id"]

    store = data_store.get()

    if not (message_id in store["messages"]):
        raise InputError("The provided message_id does not exist")

    if not check_user_is_message_member(auth_user_id, message_id):
        raise InputError("You are not part of the specified channel/dm")

    if not check_user_is_message_owner(auth_user_id, message_id):
        raise AccessError("You do not have permission to pin this message")

    if store["messages"][message_id].is_pinned:
        raise InputError("Message is already pinned")

    store["messages"][message_id].is_pinned = True

    data_store.set(store)
    return {}
    store["messages"][message_id].is_pinned = True


def message_unpin_v1(token, message_id):
    """given message is marked as unpinned

    Args:
        token (string): user's token
        message_id (int): message to be unpinned

    Raises:
        InputError: message does no exist
        InputError: user has no access to the message
        AccessError: user does not have permission to unpin message
        InputError: message is already unpinned

    Returns:
        empty dictionary
    """
    auth_user_id = decode_token(token)["auth_user_id"]
    store = data_store.get()

    if not (message_id in store["messages"]):
        raise InputError("The provided message_id does not exist")

    if not check_user_is_message_member(auth_user_id, message_id):
        raise InputError("You are not part of the specified channel/dm")

    if not check_user_is_message_owner(auth_user_id, message_id):
        raise AccessError("You do not have permission to unpin this message")

    if not store["messages"][message_id].is_pinned:
        raise InputError("Message is not pinned")

    store["messages"][message_id].is_pinned = False

    data_store.set(store)

    return {}



########################################
###### - - HELPER FUNCTIONS - - #######
######################################
def validate_message(message):
    if len(message) >= 1 and len(message) <= 1000:
        return
    raise InputError(description="incorrect message length")

def validate_mid(messages, message_id):
    for message in messages.values():
        if message_id == message.id:
            return
    raise InputError(description="incorrect message id")


def message_access(store, message_id, u_id):
    message = store['messages'][message_id]
    if u_id == message.get_owner():
        return
    if message.get_parent_type() == "channel":
        if message.parent.id == u_id:
            return

    if message.get_parent_type() == "dm":
        if message.parent.id == u_id:
            return

    raise AccessError(description="no access to message")

def check_user_is_message_member(u_id, message_id):
    '''
    Returns True if the u_id provided is a member of the message specified by message id
    returns False otherwise
    '''
    store = data_store.get()
    message_members = store["messages"][message_id].parent.all_members

    if u_id in message_members:
        return True
    return False


def check_user_is_message_owner(u_id, message_id):
    '''
    Returns True if the u_id provided is a member of the message specified by message id
    returns False otherwise
    '''
    store = data_store.get()
    message_owners = store["messages"][message_id].parent.owner_members

    if u_id in message_owners:
        return True
    return False


def notify_tagged_user(user_tagged, sender_handle, message_text, parent_id, parent_name, is_channel):
    """
    Updates the notifications list with a tag notification of the form:
    {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message":
            "{User's handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
    }
    where channel_id is the id of the channel that the event happened in, and is -1 if it is being sent to a DM.
    dm_id is the DM that the event happened in, and is -1 if it is being sent to a channel.

    Args:
        user_tagged (User): The user tagged in the massage
        sender_handle (string): The handle of the user who sent the message
        message_text (string): The message sent containing the tag
        parent_id (int): The channel/dm id the message is sent to
        parent_name (string): The name of the channel/dm the message is sent to
        is_channel (bool): True if the parent is a channel, False if it is a dm

    Returns:
        None
    """
    store = data_store.get()
    trunc_msg = message_text[0:20]

    if is_channel:
        channel_id = parent_id
        dm_id = -1
    else:
        channel_id = -1
        dm_id = parent_id

    notification = {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message": f"{sender_handle} tagged you in {parent_name}: {trunc_msg}"
    }
    store["users"][user_tagged].notifications.append(notification)
    data_store.set(store)
