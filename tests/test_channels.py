import pytest
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
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

@pytest.fixture #user1 creates a public channel
def private_second_channel_user1(user_1):
    return channels_create_v1(user_1['auth_user_id'], 'User_1_Private', False)

@pytest.fixture #user2 creates a private channel
def private_channel_user2(user_2):
    return channels_create_v1(user_2['auth_user_id'], 'Private', False)

@pytest.fixture #user2 joined a public channel
def joined_channel(user_1, user_2, public_channel_user1):
    return channel_join_v1(user_2['auth_user_id'], public_channel_user1['channel_id'])


def test_create_public_channel(user_2):
    '''
    Test to check if creating a new public channel return the channel-id of that channel
    Assumption: The auth_user_id is correct
    '''
    assert channels_create_v1(user_2['auth_user_id'], 'public_channel', True) == {
        'channel_id': 1
    }
    clear_v1()
    

def test_create_private_channel(user_2):
    '''
    Test to check if creating a new private channel will return the correct channel_id
    Assumption: The auth_user_id is correct
    '''
    assert channels_create_v1(user_2['auth_user_id'], 'test_channel', False) == {
        'channel_id': 1
    }
    clear_v1()
    
    
def test_create_channel_invalid_name_1(user_2):
    '''
    Test to check if creating a channel with an invalid name of less than 1 character raises an Input Error
    Assumption: The auth_user_id is correct
    '''
    with pytest.raises(InputError):
        assert channels_create_v1(user_2['auth_user_id'], '', True)
    clear_v1()
        
        
def test_create_channel_invalid_name_2(user_2):
    '''
    Test to check if creating a new channel with an invalid name of more than 20 characters raises an Input Error
    Assumption: The auth_user_id is correct
    '''
    with pytest.raises(InputError):
        assert channels_create_v1(user_2['auth_user_id'], 'abcdefghijklmnopqrstuv', True)
    clear_v1()

def test_create_multiple_channel(user_2):
    '''
    Test to check if creating multiple channels will return sequential channel_ids
    Assumption: the channels will not be sorted by their name in alphabetical order
    '''
    assert channels_create_v1(user_2['auth_user_id'], 'channel_1', True) == {
        'channel_id': 1
    }
    assert channels_create_v1(user_2['auth_user_id'], 'channel_2', True) == {
        'channel_id': 2
    }
    clear_v1()
    

def test_channel_list_private(user_2, private_channel_user2):
    '''
    Test to check if a member of a private channel can list all the channels he is a member of
    Assumption: The auth_user_id is correct
    Assumption: The user is only a member of one channel
    '''
    assert channels_list_v1(user_2['auth_user_id']) == {
        'channels': [
            {
                'channel_id': private_channel_user2['channel_id'],
                'channel_name': 'Private',
            }
        ]
    }
    clear_v1()
    

def test_channel_list_public(user_1, public_channel_user1):
    '''
    Test to check if a member of a public channel can list all the channels he is a member of
    Assumption: The auth_user_id is correct
    Assumption: The user is only a member of one channel
    '''
    assert channels_list_v1(user_1['auth_user_id']) == {
        'channels': [
            {
                'channel_id': public_channel_user1['channel_id'],
                'channel_name': 'Public',
            }
        ]
    }
    clear_v1()
    
def test_channel_list_empty(user_2):
    '''
    Test to check if an empty list of dictionaries is returned if the user is not a member of any channels
    Assumption: The auth_user_id is correct
    '''
    assert channels_list_v1(user_2['auth_user_id']) == {
        'channels': []
    }
    clear_v1()
    
    
def test_channel_list_multiple_created(user_1, public_channel_user1, private_second_channel_user1):
    '''
    Test to check if a list of dictionaries containing channel details is correctly generated, 
    when the user creates and is the owner of multiple channels
    Assumption: The auth_user_id is correct
    '''
    assert channels_list_v1(user_1['auth_user_id']) == {
        'channels': [
            {
                'channel_id':public_channel_user1['channel_id'],
                'channel_name': 'Public',
            }, 
            {
                'channel_id': private_second_channel_user1['channel_id'],
                'channel_name': 'User_1_Private',
            }
        ]
    }
    clear_v1()
    

def test_channel_list_joined(user_2, public_channel_user1, joined_channel):
    '''
    Test to check if a list of dictionary containing channel details is correctly generated, 
    when the user has joined a public channel
    Assumption: The auth_user_id is correct
    '''
    assert channels_list_v1(user_2['auth_user_id']) == {
        'channels': [
            {
                'channel_id': public_channel_user1['channel_id'],
                'channel_name': 'Public',
            }
        ]
    }
    clear_v1()

    
def test_channel_list_multiple_created_joined(user_1, user_2, private_channel_user2, joined_channel):
    '''
    Test to check if a list of dictionaries containing channel details is correctly generated, 
    when the user has created a channel and joined another channel
    Assumption: The auth_user_id is correct
    '''
    
    assert channels_list_v1(user_2['auth_user_id']) == {
        'channels': [
            {
                'channel_id': 1,
                'channel_name': 'Private',
            },
            {
                'channel_id': 2,
                'channel_name': 'Public',
            },
        ]
    }
    clear_v1()