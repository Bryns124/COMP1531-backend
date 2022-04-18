"""
Notifications contains the functionality to get and return the user's 20 most recent notifications.
    notifications_get_v1: Gets and returns the 20 most recent notifications.
"""
from src.data_store import data_store
from src.helper import decode_token, validate_token
from src.error import AccessError


def notifications_get_v1(token):
    """
    Gets the and returns the 20 most recent notifications.
    Args:
        token: The token of the user calling the messages.

    Returns:
        _type_: _dictionary_
    """
    store = data_store.get()

    # if not validate_token(token):
    #     raise AccessError(description="The token is invalid.")

    u_id = decode_token(token)['auth_user_id']

    notifications_message = store["users"][u_id].notifications[::-1]
    notifications_trunc = notifications_message[0:20]
    return {"notifications": notifications_trunc}
