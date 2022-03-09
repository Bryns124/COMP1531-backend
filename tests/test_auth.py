import pytest
from src.data_store import data_store
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

@pytest.fixture
def user_1():
    return auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    
# Testing when the registering email is invalid
def test_register_invalid_email():
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

# Testing when the registering email has already been used by another user
def test_register_email_already_used():
    auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    clear_v1()

# Testing when a new email is registered that it returns a unique user ID
def test_register_returns_unique_ID():
    assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le") != auth_register_v1("jamesnguyen@gmail.com", "password789", "James", "Nguyen")
    clear_v1()

# Testing when the registered len(password) < 6 characters
def test_password_length_less_than_6():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "pass", "Bryan", "Le")
    clear_v1()

# Testing when the registered name_first < 1
def test_first_name_length_less_than_1():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "", "Le")
    clear_v1()
        
# Testing when the registered name_first > 50
def test_first_name_length_more_than_50():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn", "Le")
    clear_v1()
        
# Testing when the registered name_last < 1
def test_last_name_length_less_than_1():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "")
    clear_v1()

# Testing when the registered name_last > 50
def test_last_name_length_more_than_50():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn")

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
    # Testing that the handle cuts off at more than 20 characters
    assert len(handle_str1) <= 20
    assert len(handle_str3) <= 20
    # Testing that a unique handle is created for a new user with the same first name and last name
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
    handle4 = 'abcdef2'
    handle5 = 'abcdef3'
    handle6 = 'abcdef4'
    handle7 = 'abcdef5'
    handle8 = 'abcdef6'
    handle9 = 'abcdef7'
    handle10 = 'abcdef8'
    handle11 = 'abcdef9'
    handle12 = 'abcdef10'

    u_id1 = auth_register_v1('abcdef1@email.com', 'password123', first, last)['auth_user_id']
    u_id2 = auth_register_v1('abcdef2@email.com', 'password456', first, last)['auth_user_id']
    u_id3 = auth_register_v1('abcdef3@email.com', 'password789', first, last)['auth_user_id']
    u_id4 = auth_register_v1('abcdef4@email.com', 'password123', first, last)['auth_user_id']
    u_id5 = auth_register_v1('abcdef5@email.com', 'password456', first, last)['auth_user_id']
    u_id6 = auth_register_v1('abcdef6@email.com', 'password789', first, last)['auth_user_id']
    u_id7 = auth_register_v1('abcdef7@email.com', 'password123', first, last)['auth_user_id']
    u_id8 = auth_register_v1('abcdef8@email.com', 'password456', first, last)['auth_user_id']
    u_id9 = auth_register_v1('abcdef9@email.com', 'password789', first, last)['auth_user_id']
    u_id10 = auth_register_v1('abcdef10@email.com', 'password789', first, last)['auth_user_id']
    u_id11 = auth_register_v1('abcdef11@email.com', 'password789', first, last)['auth_user_id']
    u_id12 = auth_register_v1('abcdef12@email.com', 'password789', first, last)['auth_user_id']

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
        if k['u_id'] == u_id4:    
            assert k['email'] == 'abcdef4@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle4
        if k['u_id'] == u_id5:
            assert k['email'] == 'abcdef5@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle5
        if k['u_id'] == u_id6:
            assert k['email'] == 'abcdef6@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle6
        if k['u_id'] == u_id7:
            assert k['email'] == 'abcdef7@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle7
        if k['u_id'] == u_id8:
            assert k['email'] == 'abcdef8@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle8
        if k['u_id'] == u_id9:
            assert k['email'] == 'abcdef9@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle9
        if k['u_id'] == u_id10:
            assert k['email'] == 'abcdef10@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle10
        if k['u_id'] == u_id11:
            assert k['email'] == 'abcdef11@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle11
        if k['u_id'] == u_id12:
            assert k['email'] == 'abcdef12@email.com'
            assert k['name_first'] == first
            assert k['name_last'] == last
            assert k['handle_str'] == handle12
            
