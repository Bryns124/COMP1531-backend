import pytest
from src.channels import channels_listall_v1, channels_create_v1
from src.auth import auth_register_v1
from src.channel import channel_join_v1
from src.other import clear_v1
from src.error import AccessError, InputError


@pytest.fixture
def user_1():
    return auth_register_v1('alice@gmail.com', '123456', 'Alice', 'Wan') 

@pytest.fixture
def user_2():
    return auth_register_v1('adi@gmail.com', 'abcdef', 'Adiyat', 'Rahman') 

@pytest.fixture #user1 creates a public channel
def public_channel_user1(user_1):
    return channels_create_v1(user_1['auth_user_id'], 'Public', True)

@pytest.fixture #user2 creates a private channel
def private_channel_user2(user_2):
    return channels_create_v1(user_2['auth_user_id'], 'Private', False)

@pytest.fixture #user2 joined a public channel
def joined_channel(user_2, public_channel_user1):
    return channel_join_v1(user_2['auth_user_id'], public_channel_user1['channel_id'])


def test_create_public_channel(user_2):
    assert channels_create_v1(user_2['auth_user_id'], 'public_channel', True) == {
        'channel_id': 1
    }
    clear_v1()
    

def test_create_private_channel(user_2):
    assert channels_create_v1(user_2['auth_user_id'], 'test_channel', False) == {
        'channel_id': 1
    }
    clear_v1()
    
    
def test_create_channel_invalid_name_1(user_2):
    with pytest.raises(InputError):
        assert channels_create_v1(user_2['auth_user_id'], '', True)
    clear_v1()
        
        
def test_create_channel_invalid_name_2(user_2):
    with pytest.raises(InputError):
        assert channels_create_v1(user_2['auth_user_id'], 'abcdefghijklmnopqrstuv', True)
    clear_v1()

def test_create_multiple_channel(user_2):
    assert channels_create_v1(user_2['auth_user_id'], 'channel_1', True) == {
        'channel_id': 1
    }
    assert channels_create_v1(user_2['auth_user_id'], 'channel_2', True) == {
        'channel_id': 2
    }
    clear_v1()
    
        