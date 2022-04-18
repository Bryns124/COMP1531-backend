from re import I
import pytest
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.helper import SECRET
from src.config import port, url
import json
from flask import Flask
import requests
import urllib
import jwt
import requests

BASE_URL = url


@pytest.fixture
def user_1():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "alice@gmail.com",
        "password": "1234567890",
        "name_first": "Alice",
        "name_last": "Wan"
    })
    return r.json()


@pytest.fixture
def user_2():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "adi@gmail.com",
        "password": "abcdefghijk",
        "name_first": "Adiyat",
        "name_last": "Rahman"
    })
    return r.json()


@pytest.fixture
def user_3():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "michael@gmail.com",
        "password": "1234567788",
        "name_first": "Michael",
        "name_last": "Chai"
    })
    return r.json()


requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_users_all_2_users(clear, user_1, user_2):
    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1['token']
    })

    payload = response.json()
    assert payload["users"] == [{
        'u_id': user_1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
    },
        {
        'u_id': user_2['auth_user_id'],
        'email': "adi@gmail.com",
        'name_first': "Adiyat",
        'name_last': "Rahman",
        'handle_str': "adiyatrahman"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_users_all_1_user(clear, user_1):
    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1['token']
    })

    payload = response.json()
    assert payload['users'] == [{
        'u_id': user_1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_users_all_3_users(clear, user_1, user_2, user_3):
    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })

    payload = response.json()
    assert payload["users"] == [{
        'u_id': user_1['auth_user_id'],
        'email': "alice@gmail.com",
        'name_first': "Alice",
        'name_last': "Wan",
        'handle_str': "alicewan"
    },
        {
        'u_id': user_2['auth_user_id'],
        'email': "adi@gmail.com",
        'name_first': "Adiyat",
        'name_last': "Rahman",
        'handle_str': "adiyatrahman"
    },
        {
        'u_id': user_3['auth_user_id'],
        'email': "michael@gmail.com",
        'name_first': "Michael",
        'name_last': "Chai",
        'handle_str': "michaelchai"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_user_profile_valid_user_1(clear, user_1):
    response = requests.get(f"{BASE_URL}/user/profile/v1", params={
        "token": user_1["token"],
        "u_id": user_1["auth_user_id"]
    })
    payload = response.json()
    assert payload == {
        'user': {
            'u_id': user_1['auth_user_id'],
            'email': "alice@gmail.com",
            'name_first': "Alice",
            'name_last': "Wan",
            'handle_str': "alicewan"
        }
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_user_profile_valid_user_2(clear, user_1, user_2):
    response = requests.get(f"{BASE_URL}/user/profile/v1", params={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })
    payload = response.json()
    assert payload == {
        'user': {
            'u_id': user_2['auth_user_id'],
            'email': "adi@gmail.com",
            'name_first': "Adiyat",
            'name_last': "Rahman",
            'handle_str': "adiyatrahman"
        }
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_user_profile_invalid(clear, user_1):
    r = requests.get(f"{BASE_URL}/user/profile/v1", params={
        "token": user_1["token"],
        "u_id": 200
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setemail_valid(clear, user_1):
    new_email = "alicenew@gmail.com"
    r = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        "token": user_1['token'],
        "email": new_email
    })
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setemail_invalid_1(clear, user_1):
    new_email = "alicenew@gmail"
    r = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        "token": user_1['token'],
        "email": new_email
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setemail_invalid_2(clear, user_1, user_2):
    new_email = "adi@gmail.com"
    r = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        "token": user_1['token'],
        "email": new_email
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_valid(clear, user_1):
    new_handle = "unfertileegg"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_not_alphanumeric(clear, user_1):
    new_handle = "unfertile&&egg"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_length_short(clear, user_1):
    new_handle = "un"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_length_long(clear, user_1):
    new_handle = "abcdefjhijklmnopqrtuvwxyz"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_3(clear, user_1, user_2):
    new_handle = "alicewan"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setname_valid(clear, user_1):
    new_first_name = "Unfertile"
    new_last_name = "Egg"
    r = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        "token": user_1['token'],
        "name_first": new_first_name,
        "name_last": new_last_name
    })
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setname_firstname_long(clear, user_1):
    new_first_name = "Abcdefghijklmnopqertuvwxyzabcdefghijklmnopqertuvwxyz"
    new_last_name = "Egg"
    r = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        "token": user_1['token'],
        "name_first": new_first_name,
        "name_last": new_last_name
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setname_lastname_long(clear, user_1):
    new_first_name = "Unfertile"
    new_last_name = "Abcdefghijklmnopqertuvwxyzabcdefghijklmnopqertuvwxyz"
    r = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        "token": user_1['token'],
        "name_first": new_first_name,
        "name_last": new_last_name
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_user_profile_removed_user(clear, user_1, user_2):
    request_delete = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })
    assert request_delete.status_code == 200

    response = requests.get(f"{BASE_URL}/user/profile/v1", params={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    payload = response.json()
    assert payload == {
        'user': {
            'u_id': user_2['auth_user_id'],
            'email': "adi@gmail.com",
            'name_first': "Removed",
            'name_last': "user",
            'handle_str': "adiyatrahman"
        }
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})
