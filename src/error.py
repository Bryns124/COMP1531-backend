from werkzeug.exceptions import HTTPException
from src.data_store import data_store\



class AccessError(HTTPException):
    code = 403
    message = 'No message specified'


class InputError(HTTPException):
    code = 400
    message = 'No message specified'


def is_channel_valid(channel_id):
    from src.helper import channel_validity
    store = data_store.get()
    if not channel_validity(channel_id, store):
        raise InputError(
            description="The channel id you have entered is not valid.")


def is_length_valid(length):
    if length < 0:
        raise InputError(
            description="The length of the standup must be greater than 0"
        )


def is_standup_active(channel_id):
    store = data_store.get()
    if not store['channels'][channel_id].active_standup == None:
        return True
    return False


def is_user_in_channel(auth_user_id, channel_id):
    from src.helper import already_member
    store = data_store.get()
    if not already_member(auth_user_id['auth_user_id'], channel_id, store):
        raise AccessError(
            description="The user is not apart of the input channel.")
