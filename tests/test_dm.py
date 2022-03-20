import pytest
from src.dm import dm_create_v1, dm_list_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
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

BASE_URL = f"http://127.0.0.1:{port}/"


@pytest.fixture
def user_1():
    r = request.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "alice@gmail.com",
        "password": "123456",
        "name_first": "Alice",
        "name_last": "Wan"
    })
    return r.json


@pytest.fixture
def user_2():
    r = request.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "adi@gmail.com",
        "password": "abcdef",
        "name_first": "Adiyat",
        "name_last": "Rahman"
    })
    return r.json

@pytest.fixture
def user_2():
    r = request.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "michael@gmail.com",
        "password": "1234567788",
        "name_first": "Michael",
        "name_last": "Chai"
    })
    return r.json



def test_dm_create_2_users(user1, user2):
    r = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids[]": [int(user2('auth_user_id'))]
    })
    payload = r.json()
    assert payload['dm_id'] == 1
    clear_v1()

def test_dm_create_3_users(user1, user2, user3):
    r = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1("token"),
        "u_ids[]": [int(user2["auth_user_id"]), int(user3["auth_user_id"])]
    })
    payload = r.json()
    assert payload['dm_id'] == 1
    assert r.status_code == 200
    clear_v1()


def test_dm_create_2_dms(user1, user2, user3, user4):
    response_1 = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1("token"),
        "u_ids[]": [int(user2('auth_user_id'))]
    })

    response_2 = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user3("token"),
        "u_ids[]": [int(user4('auth_user_id'))]
    })
    payload_1 = response_1.json()
    payload_2 = response_2.json()
    assert payload_1['dm_id'] == 1
    assert payload_2['dm_id'] == 2
    clear_v1()


def test_dm_create_invalid_ids(user1):
    invalid_id = 200
    r = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids[]": [invalid_id]
    })
    assert r.status_code == InputError.code
    clear_v1()



def test_dm_create_duplicate_ids_1(user1):
    r = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids[]": [int(user1('auth_user_id'))]
    })
    assert r.status_code == InputError.code
    clear_v1()


def test_dm_create_duplicate_ids_2(user1, user2):
    r = request.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids[]": [int(user2('auth_user_id')), int(user2('auth_user_id'))]
    })
    assert r.status_code == InputError.code
    clear_v1()
