from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import AccessError, InputError 
from src.other import clear_v1
import pytest

"""Users"""
@pytest.fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test", "Mikey", "Test")
@pytest.fixture 
def user_2():
    return auth_register_v1("miguel@unsw.com", "test", "Miguel", "Test")
@pytest.fixture
def user_no_access():
    return auth_register_v1("error@unsw.com", "no_access", "no_access", "no_access")
@pytest.fixture
def user_invalid():
    return "invalid"

"""Channels"""
@pytest.fixture
def channel_public(user_1):
    return channels_create_v1(user_1["auth_user_id"], "Test Channel", True)
@pytest.fixture
def channel_private(user_no_access):
    return channels_create_v1(user_no_access["auth_user_id"], "No Access Test Channel", False)
@pytest.fixture
def invalid_channel_id():
    return "invalid_channel_id"
@pytest.fixture
def start():
    return 0
"""Clearing Datastore"""


def test_channel_messages_v1_channel_id_error(user_1, invalid_channel_id, start):
    with pytest.raises(InputError):
        channel_messages_v1(user_1["auth_user_id"], invalid_channel_id, start)
clear_v1()
def test_channel_messages_v1_invalid_start(user_1, invalid_channel_id, start):
    with pytest.raises(InputError):
        channel_messages_v1(user_1["auth_user_id"], invalid_channel_id, start)
clear_v1()
