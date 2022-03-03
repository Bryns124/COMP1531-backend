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
"""Clearing Datastore"""
@pytest.fixture
def clear():
    return clear_v1
   
def test_channel_invite_access_error(user_1, channel_private, user_no_access):    
    """
    This test checks to see that a AccessError is raised when attmepting to invite someone to a channel,
    but they do not have the access privlieges to do so. 
    Args:
        user_1 (_type_): _description_
        channel_private (_type_): _description_
        user_no_access (_type_): _description_
    """
    clear()
    with pytest.raises(AccessError):
        channel_invite_v1(user_1["auth_user_id"],channel_private, user_2["auth_user_id"])

def test_channel_invite_channel_id_error(user_1, invalid_channel_id, user_2):
    """
    This test checks to see that a InputError is raised when attemtping to invite someone to
    a channel with a invalid channel_id
    Args:
        user_1 (_type_): The u_id of the person executing the command and inviting. 
        invalid_channel_id (_type_): The invalid channel_id
        user_2 (_type_): The u_id of the person being invited
    """
    clear()
    with pytest.raises(InputError):
        channel_invite_v1(user_1["auth_user_id"], invalid_channel_id, user_2["auth_user_id"])

def test_channel_invite_u_id_error(user_1, channel_public, user_invalid):
    """
    This test checks to see that a InputError is raised when attemtping to invite someone with
    an invalid u_id.
    Args:
         user_1 (u_id): The u_id of the person executing the command and inviting. 
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.  
        user_invalid (u_id): The invalid u_id
    """
    clear()
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel_public, user_invalid) 
        
def test_channel_invite_u_id_member(user_1, channel_public, user_2):
    """
    This test checks to see that a InputError is raised when attempting invite someone 
    to a channel who is already apart of that channel.
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting. 
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.  
        user_2 (u_id): The u_id of the person that is already in the channel.
    """
    clear()
    channel_invite_v1(user_1['auth_user_id'], channel_public, user_2['auth_user_id'])
    with pytest.raises(InputError):
        channel_invite_v1(user_1['auth_user_id'], channel_public, user_2['auth_user_id'])
    
    

def test_channel_invite(user_1, channel_public, user_2):
    """
    This test verifies that when a user is invited to a channel they successfully become a member
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting. 
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.  
        user_2 (u_id): The u_id of the person being invited.
    """
    clear()
    channel_invite_v1(user_1['auth_user_id'], channel_public['channel_id'], user_2['auth_user_id'])
    assert channels_list_v1(user_2['auth_user_id'])['channels'][-1]['channel_id'] == channel_public['channel_id']
    #however need to test that the user was added sucessfully so need to check the channel details and find the user in the list of users in the channel 

    
