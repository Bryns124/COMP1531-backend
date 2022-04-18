from src.classes import Standup
from src.data_store import data_store
from src.helper import decode_token
from src.error import is_channel_valid, is_length_valid, is_standup_active, is_user_in_channel, InputError


def standup_start_v1(token, channel_id, length):
    auth_user_id = decode_token(token)
    is_channel_valid(channel_id)
    is_user_in_channel(auth_user_id, channel_id)
    is_length_valid(length)
    if is_standup_active(channel_id):
        raise InputError(description="A standup is currently active.")
    store = data_store.get()
    store['channels'][channel_id].start_standup(
        auth_user_id['auth_user_id'], length)

    return {
        "time_finish": store['channels'][channel_id].active_standup.end_time
    }


def standup_active_v1(token, channel_id):
    auth_user_id = decode_token(token)
    is_channel_valid(channel_id)
    is_user_in_channel(auth_user_id, channel_id)

    store = data_store.get()

    if not store['channels'][channel_id].active_standup:
        return {
            "is_active": False,
            "time_finish": None
        }
    return {
        "is_active": True,
        "time_finish": store['channels'][channel_id].active_standup.end_time
    }


def standup_send_v1(token, channel_id, message):

    auth_user_id = decode_token(token)
    is_channel_valid(channel_id)
    is_user_in_channel(auth_user_id, channel_id)
    if len(message) > 1000:
        raise InputError(description="Message cannot be over 1000.")
    if not is_standup_active(channel_id):
        raise InputError(description="A standup is currently not active.")

    store = data_store.get()
    store['channels'][channel_id].active_standup.message_compile(
        auth_user_id['auth_user_id'], message)
    data_store.set(store)

    return {}
