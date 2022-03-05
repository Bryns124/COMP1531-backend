import pytest

from src.channel import channel_messages_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1

@pytest.fixture()
def user_1():
    return auth_register_v1("mikey@unsw.com", "test", "Mikey", "Test")
@pytest.fixture()
def user_2():
    return auth_register_v1("miguel@unsw.com", "test", "Miguel", "Test")
@pytest.fixture()
def channel_1():
    return channels_create_v1(user_1["auth_user_id"], "Test Channel", True)
@pytest.fixture() 
def starting_value():
    return 0
    
def test_channel_messages(user_1, channel_1, starting_value):
    
    assert channel_messages_v1()
    
    #when i call this test for the first time, there should be no mesages, or we can add 1 just to start off with
    #in each case start should = 0, looking to load 50 of the most recent messages, in both cases, the end will be -1, to signify there are not more messages to load as it the function will having nothing to load past 1 message
    
    