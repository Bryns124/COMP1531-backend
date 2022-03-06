from src.channel import channel_details_v1, channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError
import pytest

@pytest.fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test123456", "Mikey", "Test")

@pytest.fixture
def user_2():
    return auth_register_v1("miguel@unsw.com", "test123456", "Miguel", "Test")

@pytest.fixture
def channel_1(user_1):
    return channels_create_v1(user_1["auth_user_id"], "A New Hope", True)

@pytest.fixture
def channel_2(user_2):
    return channels_create_v1(user_2["auth_user_id"], "Empire Strikes Back", True)

@pytest.fixture
def invalid_user_id():
    return -1

@pytest.fixture
def starting_value():
    return 0

@pytest.fixture
def invalid_channel():
    return {
        'channel_id': -1
    } 

'''
channel_details_v1(auth_user_id, channel_id) 

returns (name, is_public, owner_members, all_members)

Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
'''

def test_input_error_channel_details_v1(user_1, invalid_channel):
    # returns InputError when invalid channel_id is provided
    with pytest.raises(InputError):
        channel_details_v1(user_1['auth_user_id'], invalid_channel['channel_id'])
    clear_v1()


def test_access_error_channel_details_v1(user_2, channel_1):
    # returns AccessError when user is not a member of the channel
    with pytest.raises(AccessError):
        channel_details_v1(user_2['auth_user_id'], channel_1['channel_id'])
    clear_v1()

def test_wrong_user_id(invalid_user_id, channel_1):
    with pytest.raises(InputError):
        channel_details_v1(invalid_user_id, channel_1)
    clear_v1()

def test_correct_inputs_channel_details_v1(user_1, channel_1):
    # Tests for correct inputs
    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) == {
        'channel_name': "A New Hope", 
        'is_public': True, 
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com' , 'name_first': 'Mikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}
            ], 
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com' , 'name_first': 'Mikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}
            ]
    }
    clear_v1()

def test_private_channel_details_v1(user_1, channel_2):
    channel_join_v1(user_1['auth_user_id'], channel_2['channel_id'])
    assert channel_details_v1(user_1['auth_user_id'], channel_2['channel_id']) == {
        'channel_name': "The Empire Strikes Back", 
        'is_public':  True, 
        'owner_members': [
            {'u_id': 1, 'email': 'miguel@unsw.com' , 'name_first': 'Miguel', 'name_last': 'Test', 'handle_str': 'migueltest'}
        ], 
        'all_members': [
            {'u_id': 1, 'email': 'miguel@unsw.com' , 'name_first': 'Miguel', 'name_last': 'Test', 'handle_str': 'migueltest'},
            {'u_id': 2, 'email': 'mikey@unsw.com' , 'name_first': 'Mikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}
        ]
    }
    clear_v1()