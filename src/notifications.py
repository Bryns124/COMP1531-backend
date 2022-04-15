from src.data_store import data_store
from src.helper import decode_token, validate_token
from src.error import AccessError


def notification_get_v1(token):

    if not validate_token(token):
        raise AccessError(description= "The token is invalid.")
    
    u_id = decode_token(token)['auth_user_id']

    # notifications inside user data I THINK