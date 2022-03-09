import pytest
from src.data_store import data_store
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

@pytest.fixture
def user_1():
    return auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    
def test_register_invalid_email():
    '''
    Tests when the registering email is invalid
    '''
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmailcom", "password123", "Bryan", "Le")
        auth_register_v1("bryanle@gmial.com", "password123", "Bryan", "Le")
        auth_register_v1("bryan..le@gmail.com", "password123", "Bryan", "Le")
        auth_register_v1("bryanle@gmail", "password123", "Bryan", "Le")
        auth_register_v1("bryan/le@gmail.com", "password123", "Bryan", "Le")
        auth_register_v1("bryanle-@gmail.com", "password123", "Bryan", "Le")
        auth_register_v1("@gmail", "password123", "Bryan", "Le")
        auth_register_v1("", "password123", "Bryan", "Le")
    clear_v1()

def test_register_email_already_used():
    '''
    Tests when the registering email has already been used by another user
    '''
    auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    clear_v1()

def test_register_returns_unique_ID():
    '''
    Tests when a new email is registered that it returns a unique user ID
    '''
    assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le") != auth_register_v1("jamesnguyen@gmail.com", "password789", "James", "Nguyen")
    clear_v1()

def test_password_length_less_than_6():
    '''
    Tests when the registered len(password) < 6 characters
    '''
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "pass", "Bryan", "Le")
    clear_v1()

def test_first_name_length_less_than_1():
    '''
    Tests when the registered first name is less than 1
    '''
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "", "Le")
    clear_v1()
        
def test_first_name_length_more_than_50():
    '''
    Tests when the registered first name is more than 1
    '''
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn", "Le")
    clear_v1()
        
def test_last_name_length_less_than_1():
    '''
    Tests when the registered last name is less than 1
    '''
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "")
    clear_v1()

def test_last_name_length_more_than_50():
    '''
    Tests when the registered last name is more than 50
    '''
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn")
    clear_v1()

# Testing that the handle is generated correctly 
def test_handle_generated_correctly():
    store = data_store.get()
    auth_register_v1("bryanle1@gmail.com", "password123", "Bryan", "Le")
    auth_register_v1("bryanle2@gmail.com", "password123", "Bryan", "Le")
    auth_register_v1("bryanle4@gmail.com", "password123", "Bryan", "Leeeeeeeeeeeeeeeeeeeeeeeeeee")
    auth_register_v1("bryanle4@gmail.com", "password123", "Bryan", "Leeeeeeeeeeeeeeeeeeeeeeeeeee")
    handle_str1 = store['users'][0]['handle_str']
    handle_str2 = store['users'][1]['handle_str']
    handle_str3 = store['users'][2]['handle_str']
    handle_str4 = store['users'][3]['handle_str']
    # Tests that the handle cuts off at more than 20 characters
    assert len(handle_str1) <= 20
    assert len(handle_str3) <= 20
    # Tests that a unique handle is created for a new user with the same first name and last name
    assert handle_str1 != handle_str2
    assert handle_str3 != handle_str4

# Testing that the handle appends the number correctly for more than once instance of the handle
def test_handles_appends_correctly():
    store = data_store.get()
    first = 'abc'
    last = 'def'
    handle1 = 'abcdef'
    handle2 = 'abcdef0'
    handle3 = 'abcdef1'

    u_id1 = auth_register_v1('abcdef1@email.com', 'password123', first, last)['auth_user_id']
    u_id2 = auth_register_v1('abcdef2@email.com', 'password456', first, last)['auth_user_id']
    u_id3 = auth_register_v1('abcdef3@email.com', 'password789', first, last)['auth_user_id']

    for k in store['users']:
        if k['u_id'] == u_id1:
            assert k['email'] == 'abcdef1@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle1
        if k['u_id'] == u_id2:
            assert k['email'] == 'abcdef2@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle2
        if k['u_id'] == u_id3:
            assert k['email'] == 'abcdef3@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle3
            
