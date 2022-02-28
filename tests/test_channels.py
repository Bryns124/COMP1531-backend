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


def test_channel_list_empty(clear_data, user_id = register_user):
    assert channels_list_v1(user_id)['channels'][0]['channel_id'] == 1
    

def test_channel_list_public(clear_data, public_channel):
    assert channels_list_v1(register_user['auth_user_id'])['channels'][0]['channel_id'] == 1
    
def test_channel_list_private(clear_data, register_user):
    # assert
    pass
    
def test_channel_list_both(clear_data, register_user):
    # assert
    pass
