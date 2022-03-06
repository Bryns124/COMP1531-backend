<<<<<<< HEAD
=======
import pytest

from src.data_store import data_store
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

<<<<<<< HEAD
@pytest.fixture
def user_1():
    return auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    
# test when the registering email is invalid
=======
# Testing when the registering email is invalid
>>>>>>> 717763f68d342c8c4802154b2c670941ffc19a62
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

# Testing that a new registered email returns a unqiue user ID
def test_register_returns_unique_ID():
    assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le") != auth_register_v1("jamesnguyen@gmail.com", "password789", "James", "Nguyen")
    clear_v1()

# Testing when the registered length of the password is less than 6 characters
def test_password_length_less_than_6():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "pass", "Bryan", "Le")
    clear_v1()

# Testing when the registered first name is less than 1
def test_first_name_length_less_than_1():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "", "Le")
    clear_v1()
        
# Testing when the registered first name is more than 50
def test_first_name_length_more_than_50():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn", "Le")
    clear_v1()
        
# Testing when the registered last name is less than 1
def test_last_name_length_less_than_1():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "")
    clear_v1()

# Testing when the registered last name is more than 50
def test_last_name_length_more_than_50():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn")
<<<<<<< HEAD

# test when login email is invalid
def test_login_invalid_email():
    with pytest.raises(InputError):
        auth_login_v1("bryanle", "password123")
        auth_login_v1("bryanle@gmailcom", "password123")
        auth_login_v1("bryanle@gmial.com", "password123")
        auth_login_v1("bryan..le@gmail.com", "password123")
        auth_login_v1("bryanle@gmail", "password123")
        auth_login_v1("bryan/le@gmail.com", "password123")
        auth_login_v1("bryanle-@gmail.com", "password123")
        auth_login_v1("@gmail", "password123")
        auth_login_v1("", "password123")
    clear_v1()
        
# test when login email is incorrect
def test_login_incorrect_email():
    with pytest.raises(InputError):
        auth_login_v1("notbryan.le@gmail.com", "password123")
    clear_v1()
        
# test when login password is incorrect
def test_login_incorrect_password():
    with pytest.raises(InputError):
        auth_login_v1("bryanle@gmail.com", "password456")
    clear_v1()
    
# test registered account is logged in correctly
def test_login_correct(user_1):
    assert auth_login_v1("bryanle@gmail.com", "password123") == user_1
    clear_v1()
>>>>>>> 33ebd9e9a0d59c4260b48affaa21a1a96416de0c
=======
    clear_v1()

# Testing that the handle is generated correctly 
def test_handle():
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
>>>>>>> 717763f68d342c8c4802154b2c670941ffc19a62
