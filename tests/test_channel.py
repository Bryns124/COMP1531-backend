from src.channel import channel_messages_v1, channel_invite_v1, channel_details_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1, auth_login_v1
from src.error import AccessError, InputError 

@fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test", "Mikey", "Test")
@fixture 
def user_2():
    return auth_register_v1("miguel@unsw.com", "test", "Miguel", "Test")

@fixture
def channel_1():
    return channels_create_v1(user_1["auth_user_id"], "Test Channel", True)
   
def test_channel_invite_access_error(user_1, channel_1, user_2):    
    with pytest.raises(AccessError):
        assert 
        
def test_channel_invite_input_error(user_1, channe_1, user_2):
    with pytest.raise(InputError):
    
def test_channel_invite(user_1, channel_1, user_2):
    """
    :auth_user_id: the u_id of the user executing the command
    :channel_id: the channel_id that we are creating the invite for
    :param: u_id: the u_id of the person receiving the invite 
    return: we return nothing for this iteration, the user is just added straight away. 
    """
    #however need to test that the user was added sucessfully so need to check the channel details and find the user in the list of users in the channel 
    
    
