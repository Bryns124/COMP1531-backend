from src.data_store import data_store
from src.error import AccessError, InputError
import jwt
import pickle

SECRET = "ANT"


def generate_token(u_id):
    valid_auth_user_id(u_id)
    store = data_store.get()
    for user in store['users']:
        if user['u_id'] == u_id:
            user['session_id'].append(
                len(user['session_id']) + 1)  # potential bug
    token = jwt.encode(
        {'auth_user_id': u_id, 'session_id': user['session_id'][-1]}, SECRET, algorithm="HS256")
    data_store.set(store)
    return token


def decode_token(token):
    token_data = jwt.decode(token, SECRET, algorithms="HS256")
    validate_token(token_data)
    return token_data


def validate_token(token_data):
    valid_auth_user_id(token_data['auth_user_id'])
    store = data_store.get()
    token_valid = False
    for user in store['users']:
        for session in user['session_id']:
            if token_data['session_id'] == session:
                token_valid = True

    if not token_valid:
        raise AccessError("This token is invalid.")


def valid_auth_user_id(auth_user_id):
    """_summary_
    Validates that the input auth_user_id exists in the datastore
    Args:
        auth_user_id (u_id): The input u_id

    Raises:
        AccessError: If the u_id input does not exist in the system, an access error is raised.
    """
    store = data_store.get()

    auth_user_exist = False

    for user in store['users']:
        if auth_user_id == user['u_id']:
            auth_user_exist = True

    if not auth_user_exist:
        raise AccessError("This auth_user_id does not exist in the datastore.")


def channel_validity(channel_id, store):
    """_summary_
    Checks for a valid channel
    Args:
        channel_id (channel_id): _description_
        store (datastore): _description_

    Returns:
        _Boolean: Returns if the channel exists or not.
    """
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            return True
    return False


def user_validity(u_id, store):
    """_summary_
    Checks for a valid channel
    Args:
        channel_id (channel_id): _description_
        store (datastore): _description_

    Returns:
        _Boolean: Returns if the channel exists or not.
    """
    for users in store['users']:
        if users['u_id'] == u_id:
            return True
    return False


def already_member(auth_user_id, channel_id, store):
    """_summary_
    Checks if a user is already a member of a channel
    Args:
        auth_user_id (u_id): The user id generated after auth login
        channel_id (channel_id): The id of the channel generated by channels_create
        store (datastore): stores the list of dictionaries
        that contains the details of the user and the accounts

    Returns:
        Boolean: Returns true if the user already is a member of the channel
    """
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id in channels['all_members'] or auth_user_id in channels['owner_members']:
                return True
    return False


def extract_channel_details(channel_id, store):
    """_summary_
    A method which coppies the data in the input_channel and returns it.
    Args:
        channel_id (_type_): _description_
        store (_type_): _description_

    Returns:
        _type_: _description_
    """
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channel_details = channels
    return channel_details


def save_data_store():
    with open('datastore.p', 'wb') as FILE:
        pickle.dump(data_store.get(), FILE)


def load_data_store():
    with open('datastore.p', 'rb') as FILE:
        data_store.set(pickle.load(FILE))
