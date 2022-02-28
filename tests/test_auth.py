import pytest

from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1

# LOGINS
# test when login email is invalid
def test_login_invalid_email():
    clear_v1()
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
# test when login email is incorrect
def test_login_incorrect_email():
    clear_v1()
    auth_login_v1("bryan.le@gmailcom", "password123")
    with pytest.raises(InputError):
        assert auth_login_v1("notbryan.le@gmail.com", "password123")
        
# test when login password is incorrect
def test_login_incorrect_password():
    clear_v1()
    auth_login_v1("bryan.le@gmailcom", "password123")
    with pytest.raises(InputError):
        assert auth_login_v1("bryan.le@gmailcom", "password456")

# test when
# ===========================================================================================
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
    auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    with pytest.raises(InputError):
        assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")

# test when the registering password is invalid (too short? or not strong enough?)

# test when the first name is invalid

# test when the last name is invalid

# def 