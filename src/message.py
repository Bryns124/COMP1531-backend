from src.data_store import data_store
from src.helper import decode_token, validate_token, channel_validity, already_member, generate_timestamp
from src.error import AccessError, InputError
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
    decode_token(token)
    if not channel_validity(channel_id, store):
        raise InputError(description="The channel you have entered is invalid")
    u_id = decode_token(token)['auth_user_id']

    if not already_member(u_id, channel_id, store):
        raise AccessError(description="User is not a member of the channel")

    validate_message(message)

    message_id = store['messages']

    if store['messages'] == []:
        message_id = 1
    else:
        message_id = len(store['messages']) + 1

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel['messages_list'].append(message_id)

    message_body = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_sent": generate_timestamp(),
        "is_ch_message": True,
    }
    store['messages'].append(message_body)

    data_store.set(store)
    return {"message_id": message_id}
# {message_id}

#{token, channel_id, message}

# def message_edit_v1(token, message_id, message):
#     """edits a message based on the message id

#     Args:
#         token (string): user's token
#         channel_id (int): channel id of where the message will be sent
#         message (string): contains the message

#     Returns:
#         dictionary: empty dictionary
#     """
#     validate_token(token)
#     validate_message(message)
#     store = data_store.get()

#     for message in store['messages']:
#         if message['message_id'] == message_id:
#             message['message'] == message

#     data_store.set(store)

#     return {}
# #{}
# def message_remove_v1(token, message_id):
#     """removes message based on message id
#         the message is removed from the list of message ID's
#         the "actual' message if NOT removed from datastore message

#     Args:
#         token (string): user's token
#         channel_id (int): channel id of where the message will be sent
#         message (string): contains the message

#     Returns:
#         dictionary: empty dictionary
#     """
#     validate_token(token)
#     store = data_store.get()

#     for message in store['messages']:
#         if message['message_id'] == message_id:
#             if (message['is_ch_message']):
#                 remove_ch_message(message_id)
#             else:
#                 remove_dm_message(message_id)

#     data_store.set(store)
#     return {}
# #{}
# def remove_ch_message(message_id):
#     store = data_store.get()
#     for channel in store['channels']:
#         if message_id in channel['messages_list']:
#             channel['messages_list'].remove(message_id)
#     data_store.set(store)

# def remove_dm_message(message_id):
#     store = data_store.get()
#     for dm in store['dms']:
#         if message_id in dm['messages_list']:
#             dm['messages_list'].remove(message_id)
#     data_store.set(store)


def validate_message(message):
    if len(message) >= 1 and len(message) <= 1000:
        return
    raise InputError("incorrect message length")


def message_senddm_v1(token, dm_id, message):
    store = data_store.get()
    u_id = decode_token(token)['auth_user_id']

    if not valid_dm_id(store, dm_id):
        raise InputError("dm id does not exist")

    validate_message(message)

    if not is_dm_member(store, u_id, dm_id) and not is_dm_owner(store, u_id, dm_id):
        raise AccessError("user is not part of dm")

    if store['messages'] == []:
        message_id = 1
    else:
        message_id = len(store['messages']) + 1

    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            dm['messages_list'].insert(0, message_id)

    message_body = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_sent": generate_timestamp(),
        "is_ch_message": False,
    }
    store['messages'].append(message_body)

    data_store.set(store)
    return {"message_id": message_id}
