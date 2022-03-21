import pytest
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.helper import SECRET
from src.config import port
import json
from flask import request, Flask
import urllib
import jwt
import pytest
import requests

BASE_URL = f"http://127.0.0.1:{port}/"


@pytest.fixture
def user_1():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "alice@gmail.com",
        "password": "123456",
        "name_first": "Alice",
        "name_last": "Wan"
    })
    return r.json


@pytest.fixture
def user_2():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "adi@gmail.com",
        "password": "abcdef",
        "name_first": "Adiyat",
        "name_last": "Rahman"
    })
    return r.json

@pytest.fixture
def user_3():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "michael@gmail.com",
        "password": "1234567788",
        "name_first": "Michael",
        "name_last": "Chai"
    })
    return r.json


def test_users_all_2_users(user1, user2):
    response = requests.get(f"{BASE_URL}/users/all/v1", json = {
        "token": user1["token"]
    })

    payload = response.json()
    assert payload["users"] == [{
        'u_id' : user1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
        },
        {
        'u_id' : user2['auth_user_id'],
        'email': "adi@gmail.com",
        'name_first': "Adiyat",
        'name_last': "Rahman",
        'handle_str': "adiyatrahman"
        }]
    clear_v1()


def test_users_all_1_user(user1):
    response = requests.get(f"{BASE_URL}/users/all/v1", json = {
        "token": user1["token"]
    })

    payload = response.json()
    assert payload["users"] == [{
        'u_id' : user1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
        }]
    clear_v1()

def test_users_all_3_users(user1, user2, user3):
    response = requests.get(f"{BASE_URL}/users/all/v1", json = {
        "token": user1["token"]
    })

    payload = response.json()
    assert payload["users"] == [{
        'u_id' : user1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
        },
        {
        'u_id' : user2['auth_user_id'],
        'email': "adi@gmail.com",
        'name_first': "Adiyat",
        'name_last': "Rahman",
        'handle_str': "adiyatrahman"
        },
        {
        'u_id' : user3['auth_user_id'],
        'email': "michael@gmail.com",
        'name_first': "Michael",
        'name_last': "Chai",
        'handle_str': "michaelchai"
        }]
    clear_v1()

def test_user_profile_valid_user_1(user1):
    response = requests.get(f"{BASE_URL}/user/profile/v1", json = {
        "token": user1["token"],
        "u_id": user1["auth_user_id"]
    })
    payload = response.json()
    assert payload == {
        'u_id' : user1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
        }
    clear_v1()

def test_user_profile_valid_user_2(user1, user2):
    response = requests.get(f"{BASE_URL}/user/profile/v1", json = {
        "token": user1["token"],
        "u_id": user2["auth_user_id"]
    })
    payload = response.json()
    assert payload == {
        'u_id' : user2['auth_user_id'],
        'email': "adi@gmail.com",
        'name_first': "Adiyat",
        'name_last': "Rahman",
        'handle_str': "adiyatrahman"
        }
    clear_v1()

def test_user_profile_invalid(user1):
    requests.get(f"{BASE_URL}/user/profile/v1", json = {
        "token": user1["token"],
        "u_id": 200
    })
    assert requests.status_code == InputError.code
    clear_v1()


def test_setemail_valid(user1):
    new_email = "alicenew@gmail.com"
    requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = {
        "token": user1['token'],
        "email": new_email
    })
    assert requests.status_code == 200

def test_setemail_invalid_1(user1):
    new_email = "alicenew@gmail"
    requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = {
        "token": user1['token'],
        "email": new_email
    })
    assert requests.status_code == InputError.code

def test_setemail_invalid_2(user1, user2):
    new_email = "adi@gmail.com"
    requests.put(f"{BASE_URL}/user/profile/setemail/v1", json = {
        "token": user1['token'],
        "email": new_email
    })
    assert requests.status_code == InputError.code

