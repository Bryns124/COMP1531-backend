from src.data_store import data_store
from src.error import AccessError, InputError
from datetime import timezone
import datetime
import jwt
import pickle

SECRET = "ANT"


def generate_token(u_id):
    """
    Takes a input user_id and generates a token for the user.
    Args:
        u_id (int): The users u_id

    Returns:
        string: A token which contains the users u_id and session_id
    """
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
    """
    Takes in a users token and decodes it.
    Args:
        token (string): Users token.

    Returns:
        dict: Dictionary containing user's u_id and session_id.
    """
    token_data = jwt.decode(token, SECRET, algorithms="HS256")
    validate_token(token_data)
    return token_data


def validate_token(token_data):
    """
    Validates the users token information.
    Args:
        token_data (dict): Dictionary containing user's u_id and session_id

    Raises:
        AccessError: Raised when the session_id is invalid.
    """
    valid_auth_user_id(token_data['auth_user_id'])
    store = data_store.get()
    token_valid = False
    for user in store['users']:
        if user['u_id'] == token_data['auth_user_id']:
            for session in user['session_id']:
                if token_data['session_id'] == session:
                    token_valid = True

    if not token_valid:
        raise AccessError(description="This token is invalid.")


def valid_auth_user_id(auth_user_id):
    """
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
        raise AccessError(
            description="This auth_user_id does not exist in the datastore.")

# REMARK: Make sure to use these helpers everywhere!
def channel_validity(channel_id, store):
    """
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


# REMARK: It might be easier for these to return the user data directly rather
# than having to search through the datastore twice?
# You could also raise an Exception here which would prevent even more repeated
# code
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
    """
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
    """
    A method which coppies the data in the input_channel and returns it.
    Args:
        channel_id (int): ID of the channel info being looked for.
        store (dict): The current state of datastore.

    Returns:
        dict: the corresponding channel info
    """
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channel_details = channels
    return channel_details


def generate_timestamp():
    """
    Generates the times_sent for messages.
    Returns:
        int: Type cast int of the current utc timestamp.
    """
    time = datetime.datetime.now(timezone.utc)
    utc = time.replace(tzinfo=timezone.utc)
    timestamp = utc.timestamp()
    return int(timestamp)


def save_data_store():
    """
    Opens a file called datastore.p and saves the datastore within.
    """
    curr = data_store.get()
    with open('datastore.p', 'wb') as FILE:
        pickle.dump(curr, FILE)


def load_data_store():
    """
    Opens a file called datastore.p and loads it into datstore.
    """
    with open('datastore.p', 'rb') as FILE:
        data_store.set(pickle.load(FILE))
