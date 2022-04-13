from src.data_store import data_store
from src.error import AccessError, InputError
from datetime import timezone
import datetime
import jwt
import pickle
from src.classes import User, Channel

SECRET = "ANT"

class Queue():
    def __init__(self):
        self.data = []

    def enqueue(self, item):
        self.data.insert(0, item)

    def dequeue(self):
        if self.size() == 0:
            return None
        else:
            return self.data.pop()

    def size(self):
        return len(self.data)

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
    user_object = store["users"][u_id]
    s_id = user_object.set_session_id()

    token = jwt.encode(
        {'auth_user_id': u_id, 'session_id': s_id}, SECRET, algorithm="HS256")
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
    try :
        token_data = jwt.decode(token, SECRET, algorithms="HS256")
    except:
        # raise Error
        pass
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
    users = data_store.get()["users"]
    for user in users:
        if users[user].auth_user_id == token_data["auth_user_id"]:
            if users[user].check_session(token_data['session_id']):
                return True
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

    if auth_user_id in store['users']:
        return True

    raise AccessError(
        description="This auth_user_id does not exist in the datastore.")


def channel_validity(channel_id, store):
    """
    Checks for a valid channel
    Args:
        channel_id (channel_id): _description_
        store (datastore): _description_

    Returns:
        _Boolean: Returns if the channel exists or not.
    """
    if channel_id in store["channels"]:
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
    if u_id in store["users"]:
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
    channels = store["users"][auth_user_id].all_channels
    if channel_id in channels:
        return True
    return False


def is_global_owner(store):
    for users in store['users']:
        if users['u_id'] == 1:
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


def load_channel(channel_id):
    store = data_store.get()
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return channel
    raise InputError(description="Could not locate channel")


def load_user(u_id):
    store = data_store.get()
    if u_id in store["users"]:
        return True

    raise InputError(description="Could not locate user")


def load_message(message_id):
    store = data_store.get()
    for message in store['messages']:
        if message['message_id'] == message_id:
            return message
    raise InputError(description="Could not locate message")


def load_dm(dm_id):
    store = data_store.get()
    for dm in store['dms']:
        if dm['dm_id'] == dm_id:
            return dm
    raise InputError(description="Could not locate dm")
