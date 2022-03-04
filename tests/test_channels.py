import pytest
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1, channels_join_v1
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

@pytest.fixture
def clear_data():
    clear_v1()



def test_channel_list_private(clear_data, private_channel_user2):
    assert channels_list_v1(user_2['auth_user_id']) == [{
        'channel_id':[1],
        'name': ['Private'],
        'is_public': [False],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    }]
    

def test_channel_list_public(clear_data, public_channel_user1):
    assert channels_list_v1(user_1['auth_user_id']) == [{
        'channel_id':[1],
        'name': ['Public'],
        'is_public': [True],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    }]
    
def test_channel_list_empty(clear_data, user_2):
    assert channels_list_v1(user_2['auth_user_id']) == []
    
def test_channel_list_multiple_created(clear_data, user_1):
    channels_create_v1(user_1['auth_user_id'], 'Public', True)
    channels_create_v1(user_1['auth_user_id'], 'Private', False)
    
    assert channels_list_v1(user_1['auth_user_id']) == [{
        'channel_id':[1],
        'name': ['Public'],
        'is_public': [True],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    }, 
    {
        'channel_id':[2],
        'name': ['Private'],
        'is_public': [False],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    }, 
    ]
    

def test_channel_list_joined(clear_data, joined_channel):
    assert channels_list_v1(user_2['auth_user_id']) == [{
        'channel_id':[1],
        'name': ['Public'],
        'is_public': [True],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    }
    ]
    
    
def test_channel_list_multiple_joined(clear_data, user_1, user_2):
    channel_id_1 = channels_create_v1(user_1['auth_user_id'], 'Public', True)
    channel_id_2 = channels_create_v1(user_1['auth_user_id'], 'Private', False)
    
    channels_join_v1(user_2['auth_user_id'], channel_id_1)
    channels_join_v1(user_2['auth_user_id'], channel_id_2)
    
    assert channels_list_v1(user_2['auth_user_id']) == [{
        'channel_id':[1],
        'name': ['Public'],
        'is_public': [True],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    },
    {
        'channel_id':[2],
        'name': ['Private'],
        'is_public': [False],
        'channel_owner': [],
        'channel_members': [],
        'channel_messages': [],
    },
    ]
    
# def test_channel_list_multiple_created_joined(clear_data, user_1):
#     channels_create_v1(user_1['auth_user_id'], 'Public', True)
#     channels_create_v1(user_1['auth_user_id'], 'Private', False)