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

from src.user import users_all_v1


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
def user_invalid():
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET, algorithm="HS256")


@pytest.fixture
def invalid_user_id():
    return -1


@pytest.fixture
def public_channel_user1(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "Public",
        "is_public": True
    })
    return r.json()


@pytest.fixture
def create_dm_2_user(user_1, user_2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    return r.json()


@pytest.fixture
def create_dm_3_user(user_1, user_2, user_3):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_2['token'],
        "u_ids": [user_1['auth_user_id'], user_3['auth_user_id']]
    })
    return r.json()

# REMARK: Make sure you clear your datastore before the test starts, since
# otherwise you'll get cascading test fails
# Turn clearing into a fixture maybe?
def test_invalid_u_id_admin_user_remove_v1(user_invalid, user_1):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_invalid,
        "u_id": user_1["auth_user_id"]
    })

    assert request_admin_user_remove_v1.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_remove_only_owner_admin_user_remove_v1(user_1):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_1["auth_user_id"]
    })

    assert request_admin_user_remove_v1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_nonglobal_owner_admin_user_remove_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
    })
    assert request_admin_user_remove_v1.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_admin_user_remove_invalid_u_id(user_1, invalid_user_id):
    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": invalid_user_id,
    })
    assert request_admin_user_remove_v1.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_remove_user_2_admin_user_remove_v1(user_1, user_2, user_3):
    q = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })
    assert q.status_code == 200

    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })
    assert response.status_code == 200
    assert response.json()['users'] == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "name_first": "Alice",
            "name_last": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 3,
            "email": "michael@gmail.com",
            "name_first": "Michael",
            "name_last": "Chai",
            "handle_str": "michaelchai"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})

# REMARK: It'd be far nicer to have helper functions for sending all your requests
def test_remove_global_owner_admin_user_remove_v1(user_1, user_2):
    requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_2["token"]
    })

    assert response.status_code == 200
    assert response.json()["users"] == [
        {
            "u_id": 2,
            "email": "adi@gmail.com",
            "name_first": "Adiyat",
            "name_last": "Rahman",
            "handle_str": "adiyatrahman"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_admin_user_remove_removing_channel_owner(user_1, user_2, user_3, create_dm_3_user):
    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    r = requests.get(f"{BASE_URL}/dm/details/v1", params={
        "token": user_1["token"],
        "dm_id": 1
    })
    payload = r.json()
    assert payload["name"] == "adiyatrahman, alicewan, michaelchai"
    assert payload['members'] == [
        user_1['auth_user_id'],
        user_3['auth_user_id']
    ]

    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })
    assert response.status_code == 200
    assert response.json()["users"] == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "name_first": "Alice",
            "name_last": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 3,
            "email": "michael@gmail.com",
            "name_first": "Michael",
            "name_last": "Chai",
            "handle_str": "michaelchai"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_removed_admin_user_remove_v1(user_1, user_2, create_dm_2_user):

    time_sent = generate_timestamp()
    request_send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1["token"],
        "dm_id": create_dm_2_user["dm_id"],
        "message": "Birds aren't real"
    })

    request_send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2["token"],
        "dm_id": create_dm_2_user["dm_id"],
        "message": "Birds aren't real"
    })

    assert request_send.status_code == 200

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1["token"],
        "dm_id": create_dm_2_user["dm_id"],
        "start": 0
    })
    assert response.status_code == 200
    assert response.json()["messages"][0]["message_id"] == 2
    assert response.json()["messages"][0]["u_id"] == 2
    assert response.json()["messages"][0]["message"] == "Removed user"
    assert response.json()["messages"][0]["time_sent"] >= time_sent

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_messages_removed_admin_user_remove_v1(user_1, user_2, public_channel_user1):
    request_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": public_channel_user1["channel_id"],
        "u_id": user_2["auth_user_id"]
    })

    assert request_invite.status_code == 200

    time_sent = generate_timestamp()
    request_send = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_2["token"],
        "channel_id": public_channel_user1["channel_id"],
        "message": "Birds aren't real"
    })

    assert request_send.status_code == 200

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1["token"],
        "channel_id": public_channel_user1["channel_id"],
        "start": 0
    })
    assert response.status_code == 200
    assert response.json()["messages"][0]["message_id"] == 1
    assert response.json()["messages"][0]["u_id"] == 2
    assert response.json()["messages"][0]["message"] == "Removed user"
    assert response.json()["messages"][0]["time_sent"] >= time_sent

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_retrievable_with_user_profile_admin_user_remove_v1(user_1, user_2):
    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    request_user_profile_v1 = requests.get(f"{BASE_URL}/user/profile/v1", params={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })
    assert request_user_profile_v1.status_code == 200
    payload = request_user_profile_v1.json()

    assert payload["user"] == {
        "u_id": 2,
        "email": "adi@gmail.com",
        "name_first": "Removed",
        "name_last": "user",
        "handle_str": "adiyatrahman"
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_email_and_handle_reusable_admin_user_remove_v1(user_1, user_2):
    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "adi@gmail.com",
        "password": "abcdef",
        "name_first": "Adiyat",
        "name_last": "Rahman"
    })

    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })

    payload = response.json()

    assert payload["users"] == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "name_first": "Alice",
            "name_last": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 3,
            "email": "adi@gmail.com",
            "name_first": "Adiyat",
            "name_last": "Rahman",
            "handle_str": "adiyatrahman"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_users_all_admin_user_remove_v1(user_1, user_2):
    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"]
    })

    request_users_all_v1 = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })

    assert request_users_all_v1.status_code == 200

    assert request_users_all_v1.json()["users"] == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "name_first": "Alice",
            "name_last": "Wan",
            "handle_str": "alicewan"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_invalid_u_id_admin_userpermission_change_v1(user_1, invalid_user_id):
    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": invalid_user_id,
        "permission_id": 1
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_demoting_only_global_owner_admin_userpermission_change_v1(user_1):
    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_1["auth_user_id"],
        "permission_id": 2
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_invalid_permission_id_admin_userpermission_change_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 3
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_promoting_global_owner_admin_userpermission_change_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
        "permission_id": 1
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_demoting_nonglobal_owner_admin_userpermission_change_v1(user_1, user_2):
    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 2
    })
    assert request_admin_user_remove_v1.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_nonglobal_owner_admin_userpermission_change_v1(user_1, user_2, user_3):
    request_admin_user_remove_v1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_2["token"],
        "u_id": user_3["auth_user_id"],
        "permission_id": 1
    })
    assert request_admin_user_remove_v1.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_promoting_user_2_admin_userpermission_change_v1(user_1, user_2, user_3):
    requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_2["token"],
        "u_id": user_3["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })

    payload = response.json()

    assert payload["users"] == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "name_first": "Alice",
            "name_last": "Wan",
            "handle_str": "alicewan"
        },
        {
            "u_id": 2,
            "email": "adi@gmail.com",
            "name_first": "Adiyat",
            "name_last": "Rahman",
            "handle_str": "adiyatrahman"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_promoting_user_2_admin_userpermission_change_v1_multiple_users(user_1, user_2, user_3):
    requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_3["auth_user_id"],
        "permission_id": 1
    })

    requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_3["token"],
        "u_id": user_2["auth_user_id"]
    })

    response = requests.get(f"{BASE_URL}/users/all/v1", params={
        "token": user_1["token"]
    })

    payload = response.json()

    assert payload["users"] == [
        {
            "u_id": 1,
            "email": "alice@gmail.com",
            "name_first": "Alice",
            "name_last": "Wan",
            "handle_str": "alicewan"
        }, {
            "u_id": 3,
            "email": "michael@gmail.com",
            "name_first": "Michael",
            "name_last": "Chai",
            "handle_str": "michaelchai"
        }

    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_demoting_user_1_admin_userpermission_change_v1(user_1, user_2):
    response1 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
        "permission_id": 1
    })
    assert response1.status_code == 200

    response2 = requests.post(f"{BASE_URL}/admin/userpermission/change/v1", json={
        "token": user_2["token"],
        "u_id": user_1["auth_user_id"],
        "permission_id": 2
    })
    assert response2.status_code == 200

    request_admin_user_remove_v1 = requests.delete(f"{BASE_URL}/admin/user/remove/v1", json={
        "token": user_1["token"],
        "u_id": user_2["auth_user_id"],
    })
    assert request_admin_user_remove_v1.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})
