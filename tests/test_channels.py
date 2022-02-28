import pytest

from src.channels import channels_list_v1
from src.channels import channels_create_v1
from src.auth import auth_login_v1
from src.auth import auth_register_v1
from src.error import AccessError
from src.error import InputError
from src.other import clear_v1

@pytest.fixture
def register_user():
    auth_register_v1("adi@gmail.com", "123456", "Adiyat", "Rahman")

@pytest.fixture 
def clear_data():
    clear_v1()

@pytest.fixture
def public_channel():
    channels_create_v1(register_user['auth_user_id'], 'Public', True)

@pytest.fixture    
def private_channel():
    channels_create_v1(register_user['auth_user_id'], 'Private', False)
    


def test_create_public_channel(clear_data, user_id = register_user):
    assert channels_create_v1(user_id, 'test_channel', True)['channel_id'] == 1
    

# def test_create_private_channel(clear_data, register_user):
#     assert channels_create_v1(register_user['auth_user_id'], False)['channel_id'] == 1
    
# Alternative Way
def test_create_private_channel(clear_data, user_id = register_user):
    assert channels_create_v1(user_id, 'test_channel', False)['channel_id'] == 1
    
    
def test_create_channel_invalid_name_1(clear_data, user_id = register_user):
    with pytest.raises(InputError):
        assert channels_create_v1(user_id, '', True)['channel_id'] == 1
        
        
    
def test_create_channel_invalid_name_2(clear_data, user_id = register_user):
    with pytest.raises(InputError):
        assert channels_create_v1(user_id, 'abcdefghijklmnopqrstuv', True)['channel_id'] == 1
