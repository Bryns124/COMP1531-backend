import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

# test when the registering email is invalid
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

# test when the registering email has already been used by another user
def test_register_email_already_used():
    auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    clear_v1()

# test when a new email is registered that it returns a unique user ID
def test_register_returns_unique_ID():
    assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le") != auth_register_v1("jamesnguyen@gmail.com", "password789", "James", "Nguyen")
    clear_v1()

# test when the registered len(password) < 6 characters
def test_password_length_less_than_6():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "pass", "Bryan", "Le")
    clear_v1()

# test when the registered name_first < 1
def test_first_name_length_less_than_1():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "", "Le")
    clear_v1()
        
# test when the registered name_first > 50
def test_first_name_length_more_than_50():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn", "Le")
    clear_v1()
        
# test when the registered name_last < 1
def test_last_name_length_less_than_1():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "")
    clear_v1()

# test when the registered name_last > 50
def test_last_name_length_more_than_50():
    with pytest.raises(InputError):
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn")
    clear_v1()