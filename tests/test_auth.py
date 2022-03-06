import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

# Fixture for testing incorrect login
@pytest.fixture
def user_1():
    return auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")

# Testing when the login email is invalid
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
        
# Testing when the login email is incorrect
def test_login_incorrect_email(user_1):
    with pytest.raises(InputError):
        auth_login_v1("notbryan.le@gmail.com", "password123")
    clear_v1()
        
# Testing when the login password is incorrect
def test_login_incorrect_password(user_1):
    with pytest.raises(InputError):
        auth_login_v1("bryanle@gmail.com", "password456")
    clear_v1()
    
# Testing if the registered account is logged in correctly
def test_login_correct(user_1):
    assert auth_login_v1("bryanle@gmail.com", "password123") == user_1
    clear_v1()