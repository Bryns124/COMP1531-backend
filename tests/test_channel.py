from src.channel import channel_details_v1, channel_invite_v1, channel_join_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import InputError, AccessError
import pytest

@pytest.fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test", "Mikey", "Test")

@pytest.fixture
def user_2():
    return auth_register_v1("miguel@unsw.com", "test", "Miguel", "Test")

@pytest.fixture
def channel_1():
    return channels_create_v1(user_1["auth_user_id"], "A New Hope", True)

@pytest.fixture
def channel_2():
    return channels_create_v1(user_2["auth_user_id"], "The Empire Strikes Back", True)

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

def test_input_error_channel_details_v1():
    # returns InputError when invalid channel_id is provided
    with pytest.raises(InputError):
        channel_details_v1(user_1['auth_user_id'], invalid_channel['channel_id'])


def test_access_error_channel_details_v1():
    # returns AccessError when user is not a member of the channel
    with pytest.raises(AccessError):
        channel_details_v1(user_2['auth_user_id'], channel_1['channel_id'])

def test_correct_inputs_channel_details_v1():
    # Tests for correct inputs
    assert channel_details_v1(user_1['auth_user_id'], channel_1['channel_id']) == (
        "A New Hope", 
        True, 
        [{'u_id': 1, 'email': 'mikey@unsw.com' , 'name_first': 'Mikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}], 
        [{'u_id': 1, 'email': 'mikey@unsw.com' , 'name_first': 'Miikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}]
    )
    clear_v1()

    channel_join_v1(user_1['auth_user_id'], channel_2['channel_id'])
    assert channel_details_v1(user_1['auth_user_id'], channel_2['channel_id']) == (
        "The Empire Strikes Back", 
        True, 
        [
            {'u_id': 2, 'email': 'miguel@unsw.com' , 'name_first': 'Miguel', 'name_last': 'Test', 'handle_str': 'migueltest'}
        ], 
        [
            {'u_id': 2, 'email': 'miguel@unsw.com' , 'name_first': 'Miguel', 'name_last': 'Test', 'handle_str': 'migueltest'},
            {'u_id': 1, 'email': 'mikey@unsw.com' , 'name_first': 'Mikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}
        ]
    )
    clear_v1()