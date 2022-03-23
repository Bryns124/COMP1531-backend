from distutils.command.config import config
from src.data_store import data_store
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1, remove_id_from_group
from src.auth import auth_register_v1
from src.error import InputError, AccessError
from src.other import clear_v1
from src.helper import SECRET
from src.config import port
import json
import requests
import urllib
import jwt
import pytest


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
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "michael@gmail.com",
        "password": "1234567788",
        "name_first": "Michael",
        "name_last": "Chai"
    })
    return r.json


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


'''
admin_user_remove

Given a user by their u_id, remove them from the Seams. This means they should be removed from all
channels/DMs, and will not be included in the list of users returned by users/all. Seams owners can
remove other Seams owners (including the original first owner). Once users are removed, the contents
of the messages they sent will be replaced by 'Removed user'. Their profile must still be retrievable
with user/profile, however name_first should be 'Removed' and name_last should be 'user'. The user's
email and handle should be reusable.

input error when u_id is invalid, u_id is the only global owner
access error when the authorised user is not a global owner

check if global user gets removed when there are 2
check if u_id 3 gets removed from list of u_ids 1,2,3,4,5


'''


def test_invalid_u_id_admin_user_remove_v1(invalid_user_id, user_1):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": invalid_user_id['token'],
        "u_id": user_1["auth_user_id"]
    })

    assert request_admin_user_remove_v1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


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

    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1["token"],
        "channel_id": public_channel_user1["channel_id"],
        "message": "Birds aren't real"
    })

    requests.delete(f"{BASE_URL}/admin/user/remove", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    store = data_store.get()
    assert store["messages"] == [
        {
            'message_id': 1,
            'u_id': 1,
            'message': 'Removed user',
            'time_sent': 1582426789,
            'is_ch_message': True
        }
    ]
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


'''
admin_userpermission_change_v1

Given a user by their user ID, set their permissions to new permissions described by permission_id.
'''


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
