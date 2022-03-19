from src.data_store import data_store
from src.helper import decode_token, validate_token, channel_validity, already_member
from src.error import AccessError, InputError
from datetime import timezone
import datetime


def messages_send_v1(token, channel_id, message):
    """user sends a message into channel

    Exceptions: #add later


    Args:
        token (string): user's token
        channel_id (int): channel id of where the message will be sent
        message (string): contains the message

    Returns:
        dictionary: dictionary that contains the message id
    """
    store = data_store.get()
    validate_token(token)
    channel_validity(channel_id, store)
    u_id = decode_token(token)['auth_user_id']

    if not already_member(u_id, channel_id, store):
        raise AccessError("authorised user is not a member of the channel")

    validate_message(message)

    message_id = store['messages']

    if store['messages'] == []:
        message_id = 1
    else:
        message_id = len(store['messages']) + 1

    time = datetime.datetime.now(timezone.utc)

    utc = time.replace(tzinfo=timezone.utc)
    timestamp = utc.timestamp()

    message_body = {
        "message_id": message_id,
        "u_id": u_id,
        "message": message,
        "time_sent": timestamp,
        "is_ch_message": True,
    }
    store['messages'].append(message_body)

    for channel in store['channel']:
        if channel['channel_id'] == channel_id:
            channel['messages_list'].append(message_id)
    data_store.set(store)
    return {"message": message_id}
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
    if message >= 1 and message <= 1000:
        return
    raise InputError("incorrect message length")
