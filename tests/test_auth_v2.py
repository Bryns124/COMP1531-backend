import pytest
import src.server
from src.error import AccessError, InputError
from src.config import port, url
from src.helper import SECRET
import json
from flask import Flask
import requests
import urllib
import jwt
import pytest

BASE_URL = url

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
def channel_public(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Test Channel",
        "is_public": True
    })
    return r.json()

def test_auth_register_user_created_sucessfully_v2():
    response = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    assert response.status_code == 200
    payload = response.json()
    payload["auth_user_id"] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_auth_register_user_multiple_v2():
    response1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    response2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "alice@gmail.com",
        "password": "wiefoiewjfwoe",
        "name_first": "Alice",
        "name_last": "Wan"
    })
    payload1 = response1.json()
    payload2 = response2.json()
    assert response2.status_code == 200
    payload1["auth_user_id"] == 1
    payload2["auth_user_id"] == 2
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_password_length_less_than_6_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "pass",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_first_name_length_less_than_1_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_first_name_length_more_than_50_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

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
    requests.delete(f"{BASE_URL}/clear/v1", json={})

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
    requests.delete(f"{BASE_URL}/clear/v1", json={})

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
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_login_incorrect_email(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "notbryan.le@gmail.com",
        "password": "test123456",
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_login_incorrect_password(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "mikey@unsw.com",
        "password": "password456",
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_login_after_logout(user_1):
    requests.post(f"{BASE_URL}/auth/logout/v1", json={
        "token": user_1['token']
    })

    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456"
    })

    assert r.status_code == 200
    body = jwt.decode(r.json()['token'], SECRET, algorithms="HS256")
    assert body == {
        "auth_user_id": 1,
        "session_id": 2
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_login_correct(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456"
    })
    assert r.status_code == 200
    body1 = jwt.decode(user_1['token'], SECRET, algorithms="HS256")
    assert body1 == {
        "auth_user_id": 1,
        "session_id": 1
    }
    body = jwt.decode(r.json()['token'], SECRET, algorithms="HS256")
    assert body == {
        "auth_user_id": 1,
        "session_id": 2
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})

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


def test_auth_logout_user_2(user_1, channel_public, user_2):
    requests.post(f"{BASE_URL}/auth/logout/v1", json={
        "token": user_2['token']
    })
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_auth_logout_after_login(user_1):
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456"
    })
    body = r.json()
    response = requests.post(f"{BASE_URL}/auth/logout/v1", json={
        "token": body['token']
    })
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})

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
        "channel_id": channel_public['channel_id'],
    })
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": body2['token'],
        "channel_id": channel_public['channel_id'],
    })
    details = requests.get(f"{BASE_URL}/channel/details/v2", params={
        "token": user_1['token'],
        "channel_id": int(channel_public['channel_id'])
    })
    body3 = details.json()
    for users in body3['all_members']:
        if users['u_id'] == body['auth_user_id']:
            assert users['name_first'] == name_first
            assert users['name_last'] == name_last
            assert users['handle_str'] == handle_1
        if users['u_id'] == body2['auth_user_id']:
            assert users['name_first'] == name_first_2
            assert users['name_last'] == name_last_2
            assert users['handle_str'] == handle_2
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_handles_appends_correctly(user_1, channel_public):
    handles = ["mikeytest", "abcdef", 'abcdef0', 'abcdef1', 'abcdef2', 'abcdef3', 'abcdef4',
               'abcdef5', 'abcdef6', 'abcdef7', 'abcdef8', 'abcdef9', 'abcdef10', 'abcdef11', 'abcdef12', 'abcdef13', 'abcdef14', 'abcdef15', 'abcdef16', 'abcdef17', 'abcdef18', 'abcdef19', 'abcdef20']
    for _ in range(22):
        request = requests.post(f"{BASE_URL}/auth/register/v2", json={
            "email": f"bryanle{_}@gmail.com",
            "password": "password123",
            "name_first": "abc",
            "name_last": "def"
        })
        body = request.json()
        requests.post(f"{BASE_URL}/channel/join/v2", json={
            "token": body['token'],
            "channel_id": channel_public['channel_id'],
        })
    data = requests.get(f"{BASE_URL}/channel/details/v2", params={
        "token": user_1['token'],
        "channel_id": int(channel_public['channel_id'])
    })
    body = data.json()
    for users in body['all_members']:
        assert users['handle_str'] in handles
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })

