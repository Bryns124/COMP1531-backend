import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

# REGISTERS
# test when the registering email is invalid
def test_register_invalid_email():
    clear_v1()
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmailcom", "password123", "Bryan", "Le")
        auth_register_v1("bryanle@gmial.com", "password123", "Bryan", "Le")
        auth_register_v1("bryan..le@gmail.com", "password123", "Bryan", "Le")
        auth_register_v1("bryanle@gmail", "password123", "Bryan", "Le")
        auth_register_v1("bryan/le@gmail.com", "password123", "Bryan", "Le")
        auth_register_v1("bryanle-@gmail.com", "password123", "Bryan", "Le")
        auth_register_v1("@gmail", "password123", "Bryan", "Le")
        auth_register_v1("", "password123", "Bryan", "Le")

# test when the registering email has already been used by another user
def test_register_email_already_used():
    clear_v1()
    auth_login_v1("bryanle@gmail.com", "password123")
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le") == {'auth_user_id': 1}

# test when the len(password) < 6 characters
def test_password_length_less_than_6():
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "pass", "Bryan", "Le") == {'auth_user_id': 1}

# test when the name_first < 1
def test_first_name_length_less_than_1():
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "password123", "", "Le") == {'auth_user_id': 1}
        
# test when the name_first > 50
def test_first_name_length_more_than_50():
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "password123", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn", "Le") == {'auth_user_id': 1}
        
# test when the name_last < 1
def test_last_name_length_less_than_1():
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "") == {'auth_user_id': 1}

# test when the name_last > 50
def test_last_name_length_more_than_50():
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn") == {'auth_user_id': 1}