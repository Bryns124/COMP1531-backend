from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import AccessError, InputError 
from src.other import clear_v1
import pytest

"""Users"""

@pytest.fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test123456", "Mikey", "Test")
@pytest.fixture 
def user_2():
    return auth_register_v1("miguel@unsw.com", "test123456", "Miguel", "Test")
@pytest.fixture
def user_no_access():
    return auth_register_v1("error@unsw.com", "no_access123456", "no_access", "no_access")
@pytest.fixture
def user_invalid():
    return -1

"""Channels"""
@pytest.fixture
def channel_public(user_1):
    return channels_create_v1(user_1["auth_user_id"], "Test Channel", True)
@pytest.fixture
def channel_private(user_no_access):
    return channels_create_v1(user_no_access["auth_user_id"], "No Access Test Channel", False)
@pytest.fixture
def invalid_channel_id():
    return -1
# @pytest.fixture
# def first_message():
#     return 0
"""Clearing Datastore"""


def test_channel_messages_v1_channel_id_error(user_1, invalid_channel_id):
    """
    This function tests that a id_error is raised when the user is trying to access the messages for 
    a invalid channel_id
    Args:
        user_1 (u_id): Id of the user who is attempting to read a channel's messages 
        invalid_channel_id (channel_id): The invalid channel id
        start (start): Where the user wants to start indexing the messages from 
    """
    with pytest.raises(InputError):
        channel_messages_v1(user_1["auth_user_id"], invalid_channel_id, 0)
    clear_v1()

# def test_channel_messages_v1_invalid_start(user_1, invalid_channel_id, start):
#     with pytest.raises(InputError):
#         channel_messages_v1(user_1["auth_user_id"], invalid_channel_id, start)
# clear_v1()

def test_channel_messages_v1_access_error(user_no_access, channel_public):
    """
    This function tests that a exception is raised when a user tries to read the messages 
    of a channel they do not have access to. 
    Args:
        user_no_access (u_id): Id of the user who has no access to read the channel messages
        channel_public (channel_id): Id of the channel the user is trying to access 
        start start): Starting index
    """
    with pytest.raises(AccessError):
        channel_messages_v1(user_no_access['auth_user_id'], channel_public['channel_id'], 0)
    clear_v1()

def test_channel_messages_v1(user_1, channel_public):
    """
    This test checks to see that no messages are present when after creating a channel
    Args:
        user_1 (u_id): The id of the user trying to read the messages in a channel 
        channel_public (channel_id): The channel_id the user is trying to access
        first_message (start_): Starting index of the messages
    """
    assert channel_messages_v1(user_1['auth_user_id'], channel_public['channel_id'], 0) == {
        'messages' : [], 
        'start' : 0, 
        'end' : -1 }
    clear_v1()