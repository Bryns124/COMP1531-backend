from src.data_store import data_store
from src.helper import decode_token, validate_token
from src.error import AccessError


def notifications_get_v1(token):

    store = data_store.get()

    if not validate_token(token):
        raise AccessError(description="The token is invalid.")

    u_id = decode_token(token)['auth_user_id']

    notifications_list = store["users"][u_id].notification_message
    notifications = notifications_list[0:20]
    return {"notifications": notifications}
