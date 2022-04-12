from src.data_store import data_store
from src.helper import decode_token, validate_token, channel_validity, already_member, generate_timestamp, Queue
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
    data_store.set(store)
    return new_message


def validate_message(message):
    if len(message) >= 1 and len(message) <= 1000:
        return
    raise InputError(description="incorrect message length")


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

    data_store.set(store)
    return new_dm_message


def validate_mid(messages, message_id):
    if messages == []:
        raise InputError(description="incorrect message id")
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
    decode_token(token)
    validate_message(query_str)

    message_list = []
    messages = data_store.get()["messages"]
    for m in messages:
        if query_str in messages[m].message:
            new = {
                "message_id": messages[m].id,
                "u_id" : messages[m].u_id,
                "message" : messages[m].message,
                "time_sent": messages[m].time_sent,
                "reacts" : messages[m].reacts,
                "is_pinned" : messages[m].is_pinned
            }
            message_list.append(new)

    return {
        "messages" : message_list
    }

def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    store = data_store.get()
    #auth_user_id = decode_token(token)['auth_user_id']

    if channel_id not in store["channels"] and dm_id not in store["dms"]:
        raise InputError("both channel and dm id are invalid")
    if channel_id != -1 and dm_id != -1:
        raise InputError("neither channel nor dm id are -1")
    if channel_id == -1 and dm_id == -1:
        raise InputError("no valid channel / dm is given")
    if len(message) > 1000:
        raise InputError("additional message is too long")
    if og_message_id not in store["messages"]:
        raise InputError("This message does not exist")
    # if auth_user_id not in store["messages"][og_message_id].parents.all_members:
    #     raise InputError("This message does not exist in the users channels / dms")

    new_message = message + " " + store["messages"][og_message_id].message

    if dm_id == -1:
        new = do_messages_send_v1(token, channel_id, new_message)

    if channel_id == -1:
        new = do_message_senddm_v1(token, dm_id, new_message)

    data_store.set(store)
    return {
        "shared_message_id": new.id
    }

def message_sendlater_v1(token, channel_id, message, time_sent):
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
    t = threading.Timer(
        delay, messages_send_v1, (token, channel_id, message)
    ).start()


def message_sendlaterdm_v1(token, dm_id, message, time_sent):
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

    t = threading.Timer(
        delay, message_senddm_v1, (token, dm_id, message)
    ).start()

def check_message_exists(message, auth_user_id):
    store = data_store.get()
    for m in store["messages"]:
        if store["messages"][m].message == message and auth_user_id in store["messages"][m].parent.all_members:
            return True
    raise InputError("message is not a valid message you are a part of")