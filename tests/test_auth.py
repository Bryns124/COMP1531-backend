import pytest
from src.data_store import data_store
from src.auth import auth_register_v1, auth_login_v1
from src.error import InputError
from src.other import clear_v1
from src.channel import channel_join_v1, channel_details_v1
from src.channels import channels_create_v1

# Fixture for testing incorrect login


@pytest.fixture
def user_1():
    return auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")


@pytest.fixture
def channel_public(user_1):
    return channels_create_v1(user_1["token"], "Test Channel", True)


@pytest.mark.parametrize('email_1', [("bryanle@gmailcom"), ("bryan..le@gmail.com"), ("bryanle@gmail"), ("bryanle-@gmail.com"), ("@gmail"), ("")])
def test_login_invalid_email(email_1):
    with pytest.raises(InputError):
        auth_login_v1(email_1, "password123")
    clear_v1()

# test when login email is incorrect


def test_login_incorrect_email(user_1):
    with pytest.raises(InputError):
        auth_login_v1("notbryan.le@gmail.com", "password123")
    clear_v1()

# test when login password is incorrect


def test_login_incorrect_password(user_1):
    with pytest.raises(InputError):
        auth_login_v1("bryan.le@gmailcom", "password456")
    clear_v1()

# test registered account is logged in correctly


def test_login_correct(user_1):
    assert auth_login_v1("bryanle@gmail.com",
                         "password123")['auth_user_id'] == 1
    clear_v1()


def test_user_created_successfully():
    '''
    Tests to see if user was created correctly
    '''

    auth_register_v1("bryanle@gmail.com", "password123", "Bryan", "Le")
    assert auth_login_v1("bryanle@gmail.com",
                         "password123")['auth_user_id'] == 1
    clear_v1()


@pytest.mark.parametrize('email_1', [("bryanle@gmailcom"), ("bryan..le@gmail.com"), ("bryanle@gmail"), ("bryanle-@gmail.com"), ("@gmail"), ("")])
def test_register_invalid_email(email_1):
    '''
    Tests when the registering email is invalid
    '''
    with pytest.raises(InputError):
        auth_register_v1(email_1, "password123", "Bryan", "Le")
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
    assert auth_register_v1("bryanle@gmail.com", "password123", "Bryan",
                            "Le") != auth_register_v1("jamesnguyen@gmail.com", "password789", "James", "Nguyen")
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
        auth_register_v1("bryanle@gmail.com", "password123",
                         "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn", "Le")
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
        auth_register_v1("bryanle@gmail.com", "password123", "Bryan",
                         "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn")
    clear_v1()

# Testing that the handle is generated correctly


@pytest.mark.parametrize('name_first, name_last, handle_1, name_first_2, name_last_2, handle_2', [
    ("Bryan", "Le", "bryanle0", "Bryan", "Le", "bryanle1"),
    ("Bryan", "Le", "bryanle0", "Bryan",
     "Leeeeeeeeeeeeeeeeeeeeeeeeeee", "bryanleeeeeeeeeeeeee"),
    ("Bryan", "Leeeeeeeeeeeeeeeeeeeeeeeeeee", "bryanleeeeeeeeeeeeee",
     "Bryan", "Leeeeeeeeeeeeeeeeeeeeeeeeeee", "bryanleeeeeeeeeeeeee0"),
    ("Bryannnnnnnnnnnnnnnn", "Le", "bryannnnnnnnnnnnnnnn", "Bryannnnnnnnnnnnnnnn", "Le", "bryannnnnnnnnnnnnnnn0")])
def test_handle_generated_correctly(user_1, channel_public, name_first, name_last, handle_1, name_first_2, name_last_2, handle_2):
    user1 = auth_register_v1("bryanle1@gmail.com",
                             "password123", name_first, name_last)
    user2 = auth_register_v1("bryanle2@gmail.com",
                             "password123", name_first_2, name_last_2)

    channel_join_v1(user1['token'], channel_public['channel_id'])
    channel_join_v1(user2['token'], channel_public['channel_id'])

    details = channel_details_v1(user_1['token'], channel_public['channel_id'])

    for users in details['all_members']:
        if users['u_id'] == user1['auth_user_id']:
            assert users['name_first'] == name_first
            assert users['name_last'] == name_last
            assert users['handle_str'] == handle_1
        if users['u_id'] == user2['auth_user_id']:
            assert users['name_first'] == name_first_2
            assert users['name_last'] == name_last_2
            assert users['handle_str'] == handle_2
    clear_v1()


def test_handles_appends_correctly(user_1, channel_public):
    handles = ["bryanle", "abcdef", 'abcdef0', 'abcdef1', 'abcdef2', 'abcdef3', 'abcdef4',
               'abcdef5', 'abcdef6', 'abcdef7', 'abcdef8', 'abcdef9', 'abcdef10', 'abcdef11', 'abcdef12', 'abcdef13', 'abcdef14', 'abcdef15', 'abcdef16', 'abcdef17', 'abcdef18', 'abcdef19', 'abcdef20']
    for _ in range(22):
        users = auth_register_v1(
            f"bryanle{_}@gmail.com", "password123", "abc", "def")
        channel_join_v1(users['token'], channel_public['channel_id'])

    details = channel_details_v1(user_1['token'], channel_public['channel_id'])
    for users in details['all_members']:
        assert users['handle_str'] in handles
    clear_v1()
