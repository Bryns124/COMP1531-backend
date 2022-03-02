from src.channel import channel_messages_v1, channel_invite_v1
from src.channels import channels_create_v1
from src.auth import auth_register_v1

@fixture
def user_1():
    return auth_register_v1("mikey@unsw.com", "test", "Mikey", "Test")
@fixture
def user_2():
    return auth_register_v1("miguel@unsw.com", "test", "Miguel", "Test")
@fixture
def channel_1():
    return channels_create_v1(user_1["auth_user_id"], "Test Channel", True)
    
    
    

    