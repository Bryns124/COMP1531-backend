from src.data_store import data_store
from src.error import AccessError, InputError
from datetime import timezone
import datetime
import jwt
import pickle
from src.classes import User, Channel

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
    try:
        token_data = jwt.decode(token, SECRET, algorithms="HS256")
    except:
        # raise Error
        raise AccessError(description="Token is Invalid") from AccessError
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

# Depcriated
# def user_validity(u_id, store):
#     """_summary_
#     Checks for a valid channel
#     Args:
#         channel_id (channel_id): _description_
#         store (datastore): _description_

#     Returns:
#         _Boolean: Returns if the channel exists or not.
#     """
#     if u_id in store["users"]:
#         return True
#     return False


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

# Depcriated
# def is_global_owner(store):
#     for users in store['users']:
#         if users['u_id'] == 1:
#             return True
#     return False

# Depcriated
# def extract_channel_details(channel_id, store):
#     """
#     A method which coppies the data in the input_channel and returns it.
#     Args:
#         channel_id (int): ID of the channel info being looked for.
#         store (dict): The current state of datastore.

#     Returns:
#         dict: the corresponding channel info
#     """
#     for channels in store['channels']:
#         if channels['channel_id'] == channel_id:
#             channel_details = channels
#     return channel_details


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

# Depcriated
# def load_channel(channel_id):
#     store = data_store.get()
#     for channel in store['channels']:
#         if channel['channel_id'] == channel_id:
#             return channel
#     raise InputError(description="Could not locate channel")

# REMARK: Don't forget docstrings - they're really helpful for checking out
# what a function does without having to actually read the code
def load_user(u_id):
    store = data_store.get()
    if u_id in store["users"]:
        return True

    raise InputError(description="Could not locate user")


# Deprecated
# def load_message(message_id):
#     store = data_store.get()
#     for message in store['messages']:
#         if message['message_id'] == message_id:
#             return message
#     raise InputError(description="Could not locate message")

# Depcriated
# def load_dm(dm_id):
#     store = data_store.get()
#     for dm in store['dms']:
#         if dm['dm_id'] == dm_id:
#             return dm
#     raise InputError(description="Could not locate dm")


def detect_tagged_user(message_text, users):
    """
    Searchs a given string for a tagged user of the form "@handle" where handle is a handle of
    a user listed in users.

    Args:
        message_text (string): The contents of a message being sent to a channel/dm
        users (dictionary): The members of the channel/dm where the message is being sent
                            of the form {u_id: User object}

    Returns:
        dictionary: The users tagged in the message of the form {u_id: User object}, an empty dict
                    if no users are tagged
    """
    tagged_users = {}
    if "@" not in message_text:
        return tagged_users

    handles_list = []

    for u_id in users:
        handles_list.append((u_id, '@' + users[u_id].handle))
        # handles_list.append('@' + users[u_id].handle)

    # for handle in handles_list:
    for user in handles_list:
        u_id = user[0]
        handle = user[1]
        if handle in message_text:
            tagged_users[u_id] = users[u_id]

    return tagged_users


def notify_add(user_invited, sender_handle, parent_id, parent_name, is_channel):
    store = data_store.get()

    if is_channel:
        channel_id = parent_id
        dm_id = -1
    else:
        channel_id = -1
        dm_id = parent_id

    notification = {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message": f"{sender_handle} added you to {parent_name}"
    }
    store["users"][user_invited].notifications.append(notification)
    data_store.set(store)


def notify_react(user_reacted, sender_handle, parent_id, parent_name, is_channel):
    store = data_store.get()

    if is_channel:
        channel_id = parent_id
        dm_id = -1
    else:
        channel_id = -1
        dm_id = parent_id

    notification = {
        "channel_id": channel_id,
        "dm_id": dm_id,
        "notification_message": f"{sender_handle} reacted to your message in {parent_name}"
    }
    store["users"][user_reacted].notifications.append(notification)
    data_store.set(store)

def get_reacts(message_id, u_id):
    react_list = []
    store = data_store.get()
    m = store["messages"][message_id]
    new_react = {
        "react_id": 1,
        "u_ids": m.react_ud_ids,
        "is_this_user_reacted": m.is_user_reacted(u_id)
    }
    react_list.append(new_react)
    return react_list
