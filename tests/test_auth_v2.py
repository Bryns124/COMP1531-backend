import code
from os import access
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
# from src.message import messages_send_v1
from src.other import clear_v1
from src.helper import decode_token
from src.error import InputError, AccessError
from src.helper import SECRET
from src.config import port
import json
import requests
import urllib
import jwt
import pytest

##MAY CHANGE PORT LATER##
BASE_URL = f"http://127.0.0.1:{port}/"


# Users


@pytest.fixture()
def user_1():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456",
        "name_first": "Mikey",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture
def user_2():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "miguel@unsw.com",
        "password": "test123456",
        "name_first": "Miguel",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture
def user_no_access():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "error@unsw.com",
        "password": "no_access1235667",
        "name_first": "no_access",
        "name_last": "no_access"
    })
    return r.json()


@pytest.fixture
def user_invalid():
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET, algorithm="HS256")


@pytest.fixture
def channel_public(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Test Channel",
        "is_public": True
    })
    return r.json()


@pytest.mark.parametrize('email_1', [("bryanle@gmailcom"), ("bryan..le@gmail.com"), ("bryanle@gmail"), ("bryanle-@gmail.com"), ("@gmail"), ("")])
def test_login_invalid_email(email_1):

    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": email_1,
        "password": "password123",
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


# test when login email is incorrect


def test_login_incorrect_email(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "notbryan.le@gmail.com",
        "password": "test123456",
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })

# test when login password is incorrect


def test_login_incorrect_password(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "bryan.le@gmailcom",
        "password": "password456",
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })

# test registered account is logged in correctly


def test_login_correct(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456"
    })
    body = jwt.decode(r.json()['token'], SECRET, algorithms="HS256")
    assert body == {
        "auth_user_id": 1,
        "session_id": 2
    }
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_auth_register_user_created_sucessfully_v2():
    request_register = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    request_login = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123"
    })
    assert request_register.status_code == 200
    assert request_register.json()['auth_user_id'] == request_login.json()[
        'auth_user_id']
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


@pytest.mark.parametrize('email_1', [("bryanle@gmailcom"), ("bryan..le@gmail.com"), ("bryanle@gmail"), ("bryanle-@gmail.com"), ("@gmail"), ("")])
def test_register_invalid_email_v2(email_1):
    # not sure how to fit all the invalid email cases
    request_register = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email_1,
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    assert request_register.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_register_email_already_used_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    request_register2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    assert request_register1.status_code == 200
    assert request_register2.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_register_returns_unique_ID_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    request_register2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "jamesnguyen@gmail.com",
        "password": "password789",
        "name_first": "James",
        "name_last": "Nguyen"
    })
    assert request_register1.json() != request_register2.json()
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_password_length_less_than_6_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "pass",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_first_name_length_less_than_1_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_first_name_length_more_than_50_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_last_name_length_less_than_1_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": ""
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_last_name_length_more_than_50_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


@pytest.mark.parametrize('name_first, name_last, handle_1, name_first_2, name_last_2, handle_2', [
    ("Bryan", "Le", "bryanle", "Bryan", "Le", "bryanle0"),
    ("Bryan", "Le", "bryanle", "Bryan",
     "Leeeeeeeeeeeeeeeeeeeeeeeeeee", "bryanleeeeeeeeeeeeee"),
    ("Bryan", "Leeeeeeeeeeeeeeeeeeeeeeeeeee", "bryanleeeeeeeeeeeeee",
     "Bryan", "Leeeeeeeeeeeeeeeeeeeeeeeeeee", "bryanleeeeeeeeeeeeee0"),
    ("Bryannnnnnnnnnnnnnnn", "Le", "bryannnnnnnnnnnnnnnn", "Bryannnnnnnnnnnnnnnn", "Le", "bryannnnnnnnnnnnnnnn0")])
def test_handle_generated_correctly_v2(user_1, channel_public, name_first, name_last, handle_1, name_first_2, name_last_2, handle_2):
    request_1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle1@gmail.com",
        "password": "password123",
        "name_first": name_first,
        "name_last": name_last
    })
    request_2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle2@gmail.com",
        "password": "password123",
        "name_first": name_first_2,
        "name_last": name_last_2
    })
    body = request_1.json()
    body2 = request_2.json()
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": body['token'],
        "channel_id": channel_public,
    })
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": body2['token'],
        "channel_id": channel_public,
    })
    details = requests.post(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public
    })
    body3 = details.json()
    for users in body3['all_members']:
        if users['u_id'] == request_1.json()['auth_user_id']:
            assert users['name_first'] == name_first
            assert users['name_last'] == name_last
            assert users['handle_str'] == handle_1
        if users['u_id'] == request_2.json()['auth_user_id']:
            assert users['name_first'] == name_first_2
            assert users['name_last'] == name_last_2
            assert users['handle_str'] == handle_2
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_handles_appends_correctly(user_1, channel_public):
    handles = ['abcdef', 'abcdef0', 'abcdef1', 'abcdef2', 'abcdef3', 'abcdef4',
               'abcdef5', 'abcdef6', 'abcdef7', 'abcdef8', 'abcdef9', 'abcdef10']
    for _ in range(12):
        request = requests.post(f"{BASE_URL}/auth/register/v2", json={
            "email": "bryanle{_}@gmail.com",
            "password": "password123",
            "name_first": "abc",
            "name_last": "def"
        })
        body = request.json()
        requests.post(f"{BASE_URL}/channel/join/v2", json={
<<<<<<< HEAD
            "token": body['token'],
            "channel_id": channel_public['channel_id'],
=======
            "token": body.json()['token'],
            "channel_id": channel_public,
>>>>>>> parent of 769bd69... fixed tests, corrected syntax for paths join and details, corrected test assertions, in terms of spelling
        })
    data = requests.post(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public
    })
    for users in data.json()['all_members']:
        assert users['handle_str'] == handles
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_auth_logout(user_1, channel_public):
    requests.post(f"{BASE_URL}/auth/logout/v1", json={
        "token": user_1['token']
    })
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
