from enum import auto
from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1, channel_join_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import AccessError, InputError 
from src.other import clear_v1
import pytest

"""Users"""
@pytest.fixture()
def user_1():
    return auth_register_v1("mikey@unsw.com", "test123456", "Mikey", "Test")
@pytest.fixture 
def user_2():
    return auth_register_v1("miguel@unsw.com", "test123456", "Miguel", "Test")
@pytest.fixture
def user_no_access():
    return auth_register_v1("error@unsw.com", "no_access1235667", "no_access", "no_access")
@pytest.fixture
def user_invalid():
    return "invalid"
@pytest.fixture
def invalid_user_id():
    return -1

"""Channels"""
@pytest.fixture
def channel_public(user_1):
    return channels_create_v1(user_1["auth_user_id"], "Test Channel", True)
@pytest.fixture
def channel_private_access(user_no_access):
    return channels_create_v1(user_no_access["auth_user_id"], "No Access Channel", False)
@pytest.fixture
def channel_1(user_1):
    return channels_create_v1(user_1["auth_user_id"], "A New Hope", True)
@pytest.fixture
def channel_2(user_2):
    return channels_create_v1(user_2["auth_user_id"], "Empire Strikes Back", True)
@pytest.fixture
def channel_private(user_1):
    return channels_create_v1(user_1["auth_user_id"], "Private Channel", False)
@pytest.fixture
def invalid_channel():
    return {
        'channel_id' : -1
    }
@pytest.fixture
def invalid_channel_id():
    return -1
@pytest.fixture
def starting_value():
    return 0

def test_channel_invite_access_error(user_1, channel_private_access, user_2):    
    """
    This test checks to see that a AccessError is raised when attmepting to invite someone to a channel,
    but they do not have the access privlieges to do so. 
    Args:
        user_1 (u_id): User who is not apart of the private channel
        channel_private (channel_id): The private channel_id
        user_no_access (u_id): User who is going to  be invited 
    """
    with pytest.raises(AccessError):
        channel_invite_v1(user_1["auth_user_id"],channel_private_access['channel_id'], user_2["auth_user_id"])
    clear_v1()

def test_channel_invite_channel_id_error(user_1, invalid_channel_id, user_2):
    """
    This test checks to see that a InputError is raised when attemtping to invite someone to
    a channel with a invalid channel_id
    Args:
        user_1 (_type_): The u_id of the person executing the command and inviting. 
        invalid_channel_id (_type_): The invalid channel_id
        user_2 (_type_): The u_id of the person being invited
    """
    with pytest.raises(InputError):
        channel_invite_v1(user_1["auth_user_id"], invalid_channel_id, user_2["auth_user_id"])
    clear_v1()

def test_channel_invite_u_id_error(user_1, channel_public, user_invalid):
    """
    This test checks to see that a InputError is raised when attemtping to invite someone with
    an invalid u_id.
    Args:
         user_1 (u_id): The u_id of the person executing the command and inviting. 
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.  
        user_invalid (u_id): The invalid u_id
    """
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel_public['channel_id'], user_invalid) 
        channel_invite_v1(user_invalid, channel_public['channel_id'], user_1['auth_user_id'])
    clear_v1()
        
def test_channel_invite_u_id_member(user_1, channel_public, user_2):
    """
    This test checks to see that a InputError is raised when attempting invite someone 
    to a channel who is already apart of that channel.
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting. 
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.  
        user_2 (u_id): The u_id of the person that is already in the channel.
    """
    channel_invite_v1(user_1['auth_user_id'], channel_public['channel_id'], user_2['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel_public['channel_id'], user_2['auth_user_id'])
    clear_v1()
    

def test_channel_invite(user_1, channel_public, user_2):
    """
    This test verifies that when a user is invited to a channel they successfully become a member
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting. 
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.  
        user_2 (u_id): The u_id of the person being invited.
    """
    channel_invite_v1(user_1['auth_user_id'], channel_public['channel_id'], user_2['auth_user_id'])
    assert channels_list_v1(user_2['auth_user_id'])['channels'][-1]['channel_id'] == channel_public['channel_id']
    clear_v1()

'''
channel_details_v1(auth_user_id, channel_id) 

Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.

returns a dictionary 
{
    "channel_name": name of the channel (string),
    "is_public": whether or not the channel is public (boolean),
    "owner_members": a list of dictionaries containing owner users, each dictionary being of the form: {
        "u_id": user id (string),
        "email": email (string),
        "name_first": first name (string),
        "name_last": last name (string),
        "handle_str": user handle (string)
    }
    "all_members": a list of dictionaries in the same format as above, however containing information 
    on all members of the channel
}
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

def test_wrong_user_id_channel_details_v1(invalid_user_id, channel_1):
    # returns InputError when invalid user_id is provided
    with pytest.raises(InputError):
        channel_details_v1(invalid_user_id, channel_1)
    clear_v1()

# Tests for correct inputs
def test_correct_inputs_channel_details_v1(user_1, channel_1):
    
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

# Test channel with multiple users, including non-owners
def test_multiple_user_channel_details_v1(user_1, channel_2):
    
    # Adds another user to the channel, who doesn't have owner status
    channel_join_v1(user_1['auth_user_id'], channel_2['channel_id']) 
    assert channel_details_v1(user_1['auth_user_id'], channel_2['channel_id']) == {
        'channel_name': "Empire Strikes Back", 
        'is_public':  True, 
        'owner_members': [
            {'u_id': 2, 'email': 'miguel@unsw.com' , 'name_first': 'Miguel', 'name_last': 'Test', 'handle_str': 'migueltest'}
        ], 
        'all_members': [
            {'u_id': 2, 'email': 'miguel@unsw.com' , 'name_first': 'Miguel', 'name_last': 'Test', 'handle_str': 'migueltest'},
            {'u_id': 1, 'email': 'mikey@unsw.com' , 'name_first': 'Mikey', 'name_last': 'Test', 'handle_str': 'mikeytest'}
        ]
    }
    clear_v1()

def test_channel_join_invalid_channel(user_1):
    '''
    channel_id does not refer to a valid channel
    '''
    with pytest.raises(InputError):
        channel_join_v1(user_1['auth_user_id'], -1)

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
