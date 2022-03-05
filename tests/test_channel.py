import pytest

from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1, channel_join_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import AccessError, InputError 
from src.other import clear_v1

@pytest.fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test", "Mikey", "Test")

@pytest.fixture 
def user_2():
    return auth_register_v1("miguel@unsw.com", "test", "Miguel", "Test")

@pytest.fixture
def channel_public(user_1):
    return channels_create_v1(user_1["auth_user_id"], "Public Channel", True)

@pytest.fixture
def channel_private(user_1):
    return channels_create_v1(user_1["auth_user_id"], "Private Channel", False)

def test_channel_join_invalid_channel(user_1):
    '''
    channel_id does not refer to a valid channel
    '''
    with pytest.raises(InputError):
        channel_join_v1(user_1['auth_user_id'], -1)
    clear_v1()

def test_channel_join_already_member(user_1, channel_public, channel_private):
    '''
    the authorised user is already a member of the channel
    '''
    with pytest.raises(InputError):
        channel_join_v1(user_1['auth_user_id'], channel_public['channel_id'])
        channel_join_v1(user_1['auth_user_id'], channel_private['channel_id'])
    clear_v1()

def test_channel_join_access_private(user_1, user_2, channel_private):
    '''
    channel_id refers to a channel that is private 
    and the authorised user is not already a channel member 
    and is not a global owner
    '''
    with pytest.raises(AccessError):
        channel_join_v1(user_2['auth_user_id'], channel_private['channel_id'])
    clear_v1()

def test_channel_join_success(user_1, user_2, channel_public):
    '''
    user successfully joins a public channel

    Assumption: the joined channel will be added sequentially as the last added one
    to channels list
    '''
    channel_join_v1(user_2['auth_user_id'], channel_public['channel_id'])
    user_2_channels = channels_list_v1(user_2['auth_user_id'])
    joined_channel = user_2_channels[-1]
    assert channel_public['channel_id'] == joined_channel[-1]['channel_id']

    clear_v1()

