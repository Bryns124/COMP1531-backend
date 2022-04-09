from src.data_store import data_store
from src.helper import decode_token, validate_token, channel_validity, already_member, generate_timestamp
from src.error import AccessError, InputError
from src.classes import Message
from datetime import timezone
import datetime
from src.dm import valid_dm_id, is_dm_member, is_dm_owner


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
    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']
    if not channel_validity(channel_id, store):
        raise InputError(description="The channel you have entered is invalid")
    if not already_member(u_id, channel_id, store):
        raise AccessError(description="User is not a member of the channel")
    validate_message(message)
    parent = store['channels'][channel_id]
    new_message = Message(u_id, message, generate_timestamp(),
                          parent)
    store['users'][u_id].add_msg(new_message.id, new_message)
    store['channels'][channel_id].message_list.append(new_message.id)
    store['messages'][new_message.id] = new_message
    data_store.set(store)
    return {"message_id": new_message.id}


def validate_message(message):
    if len(message) >= 1 and len(message) <= 1000:
        return
    raise InputError(description="incorrect message length")


def message_senddm_v1(token, dm_id, message):
    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError(description="dm id does not exist")

    validate_message(message)

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError(description="user is not part of dm")

    new_dm_message = Message(
        u_id, message, generate_timestamp(), store['dms'][dm_id])
    store['dms'][dm_id].message_list.append(new_dm_message.id)
    store['messages'][new_dm_message.id] = new_dm_message

    data_store.set(store)
    return {"message_id": new_dm_message.id}


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


# def remove_ch_message(store, message_id):
#     for channel in store['channels']:
#         if message_id in channel['messages_list']:
#             channel['messages_list'].remove(message_id)


# def remove_dm_message(store, message_id):
#     for dm in store['dms']:
#         if message_id in dm['messages_list']:
#             dm['messages_list'].remove(message_id)
