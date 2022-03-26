import json
import urllib
from distutils.command.config import config
import requests
import jwt
import pytest
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1, remove_id_from_group
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.helper import SECRET, generate_timestamp
from src.config import port
from flask import request, Flask


BASE_URL = f"http://127.0.0.1:{port}/"


@pytest.fixture()
def user_1():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "alice@gmail.com",
        "password": "123456",
        "name_first": "Alice",
        "name_last": "Wan"
    })
    return r.json()


@pytest.fixture
def user_2():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "adi@gmail.com",
        "password": "abcdef",
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


@pytest.fixture
def invalid_user_id():
    return jwt.encode({'auth_user_id': -1, 'session_id': 1}, SECRET, algorithm="HS256")


@pytest.fixture
def public_channel_user1(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "Public",
        "is_public": True
    })
    return r.json()


# def test_invalid_u_id_admin_user_remove_v1(invalid_user_id, user_1):
#     request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove", json={
#         "token": invalid_user_id['token'],
#         "u_id": user_1["auth_user_id"]
#     })

#     assert request_admin_user_remove_v1.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_remove_only_owner_admin_user_remove_v1(user_1):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_1["auth_user_id"]
    })

    assert request_admin_user_remove_v1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def nonglobal_owner_admin_user_remove_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
    })
    assert request_admin_user_remove_v1.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_remove_user_2_admin_user_remove_v1(user_1, user_2, user_3):
    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/users/all", json={
        "token": user_1["token"]
    })

    payload = response.json()

    assert payload == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "first_name": "Alice",
            "last_name": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 3,
            "email": "michael@gmail.com",
            "first_name": "Michael",
            "last_name": "Chai",
            "handle_str": "michaelchai"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_remove_global_owner_admin_user_remove_v1(user_1, user_2):
    requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/users/all", json={
        "token": user_2["token"]
    })

    payload = response.json()

    assert payload == [
        {
            "u_id": 2,
            "email": "adi@gmail.com",
            "first_name": "Adiyat",
            "last_name": "Rahman",
            "handle_str": "adiyatrahman"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


# fixed asserts for removed user messages
def test_messages_removed_admin_user_remove_v1(user_1, user_2, public_channel_user1):
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": public_channel_user1["channel_id"],
        "u_id": user_2["auth_user_id"]
    })

    time_sent = generate_timestamp()
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_2["token"],
        "channel_id": public_channel_user1["channel_id"],
        "message": "Birds aren't real"
    })

    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_1["token"],
        "channel_id": public_channel_user1["channel_id"],
        "start": 0
    })
    assert response["messages"][0]["message_id"] == 1
    assert response["messages"][0]["u_id"] == 2
    assert response["messages"][0]["message"] == "Removed user"
    assert response["messages"][0]["time_sent"] >= time_sent

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_retrievable_with_user_profile_admin_user_remove_v1(user_1, user_2):
    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    request_user_profile_v1 = requests.get(f"{BASE_URL}/user/profile/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })
    payload = request_user_profile_v1.json()

    assert payload == {
        "u_id": 2,
        "email": "adi@gmail.com",
        "first_name": "Removed",
        "last_name": "user",
        "handle_str": "adiyatrahman"
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_email_and_handle_reusable_admin_user_remove_v1(user_1, user_2):
    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "adi@gmail.com",
        "password": "abcdef",
        "name_first": "Adiyat",
        "name_last": "Rahman"
    })

    response = requests.get(f"{BASE_URL}/users/all", json={
        "token": user_1["token"]
    })

    payload = response.json()

    assert payload == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "first_name": "Alice",
            "last_name": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 3,
            "email": "adi@gmail.com",
            "first_name": "Adiyat",
            "last_name": "Rahman",
            "handle_str": "adiyatrahman"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_users_all_admin_user_remove_v1(user_1, user_2):
    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    request_users_all_v1 = requests.get(f"{BASE_URL}/users/all", json={
        "token": user_1["token"]
    })

    payload = request_users_all_v1.json

    assert payload == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "first_name": "Alice",
            "last_name": "Wan",
            "handle_str": "alicewan"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_invalid_u_id_admin_userpermission_change_v1(invalid_user_id):
    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": invalid_user_id["token"],
        "u_id": invalid_user_id["auth_user_id"],
        "permission_id": 1
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_demoting_only_global_owner_admin_userpermission_change_v1(user_1):
    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_1["auth_user_id"],
        "permission_id": 2
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_invalid_permission_id_admin_userpermission_change_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 3
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_promoting_global_owner_admin_userpermission_change_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
        "permission_id": 1
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_demoting_nonglobal_owner_admin_userpermission_change_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 2
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def nonglobal_owner_admin_userpermission_change_v1(user_1, user_2, user_3):
    request_admin_user_remove_v1 = requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_2["token"],
        "u_id": user_3["auth_user_id"],
        "permission_id": 1
    })
    assert request_admin_user_remove_v1.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def promoting_user_2_admin_userpermission_change_v1(user_1, user_2, user_3):
    requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_2["token"],
        "u_id": user_3["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/users/all", json={
        "token": user_1["token"]
    })

    payload = response.json()

    assert payload == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "first_name": "Alice",
            "last_name": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 2,
            "email": "adi@gmail.com",
            "first_name": "Adiyat",
            "last_name": "Rahman",
            "handle_str": "adiyatrahman"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def demoting_user_1_admin_userpermission_change_v1(user_1, user_2):
    requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    requests.put(f"{BASE_URL}/admin/userpermission/change", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
        "permission_id": 2
    })

    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
    })
    assert request_admin_user_remove_v1.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})
