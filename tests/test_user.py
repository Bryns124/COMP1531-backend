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


@pytest.fixture  # user1 creates a public channel
def public_channel_user1(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "Public",
        "is_public": True
    })
    return r.json()


@pytest.fixture  # user2 creates a private channel
def private_channel_user2(user_2):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_2["token"],
        "name": "Private",
        "is_public": False
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
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id'], user_3['auth_user_id']]
    })
    return r.json()

@pytest.fixture
def messages_send_2_channel(user_1, public_channel_user1):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": public_channel_user1['channel_id'],
        "message": "Message 1"
    })
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": public_channel_user1['channel_id'],
        "message": "Message 2"
    })
    return

@pytest.fixture
def send_multiple_dms(user_1, create_dm_3_user, create_dm_2_user):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "hello"
    })

    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 2,
        "message": "world"
    })
    return

requests.delete(f"{BASE_URL}/clear/v1", json={})




def test_users_all_2_users(user_1, user_2):
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


def test_users_all_1_user(user_1):
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


def test_users_all_3_users(user_1, user_2, user_3):
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


def test_user_profile_valid_user_1(user_1):
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


def test_user_profile_valid_user_2(user_1, user_2):
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


def test_user_profile_invalid(user_1):
    r = requests.get(f"{BASE_URL}/user/profile/v1", params={
        "token": user_1["token"],
        "u_id": 200
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setemail_valid(user_1):
    new_email = "alicenew@gmail.com"
    r = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        "token": user_1['token'],
        "email": new_email
    })
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setemail_invalid_1(user_1):
    new_email = "alicenew@gmail"
    r = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        "token": user_1['token'],
        "email": new_email
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setemail_invalid_2(user_1, user_2):
    new_email = "adi@gmail.com"
    r = requests.put(f"{BASE_URL}/user/profile/setemail/v1", json={
        "token": user_1['token'],
        "email": new_email
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_valid(user_1):
    new_handle = "unfertileegg"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_not_alphanumeric(user_1):
    new_handle = "unfertile&&egg"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_length_short(user_1):
    new_handle = "un"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_length_long(user_1):
    new_handle = "abcdefjhijklmnopqrtuvwxyz"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_sethandle_invalid_3(user_1, user_2):
    new_handle = "alicewan"
    r = requests.put(f"{BASE_URL}/user/profile/sethandle/v1", json={
        "token": user_1['token'],
        "handle_str": new_handle
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setname_valid(user_1):
    new_first_name = "Unfertile"
    new_last_name = "Egg"
    r = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        "token": user_1['token'],
        "name_first": new_first_name,
        "name_last": new_last_name
    })
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setname_firstname_long(user_1):
    new_first_name = "Abcdefghijklmnopqertuvwxyzabcdefghijklmnopqertuvwxyz"
    new_last_name = "Egg"
    r = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        "token": user_1['token'],
        "name_first": new_first_name,
        "name_last": new_last_name
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_setname_lastname_long(user_1):
    new_first_name = "Unfertile"
    new_last_name = "Abcdefghijklmnopqertuvwxyzabcdefghijklmnopqertuvwxyz"
    r = requests.put(f"{BASE_URL}/user/profile/setname/v1", json={
        "token": user_1['token'],
        "name_first": new_first_name,
        "name_last": new_last_name
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_user_profile_removed_user(user_1, user_2):
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


def user_stats_none(user_1):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert response.status_code == 200
    assert payload['user_stats']['involvement_rate'] == 0
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_one_channel(user_1, public_channel_user1):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert response.status_code == 200
    assert payload['user_stats']['involvement_rate'] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_two_channels(user_1, user2, public_channel_user1, private_channel_user2):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert response.status_code == 200
    assert payload['user_stats']['involvement_rate'] == 0.5
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_one_dm(user_1, user2, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert response.status_code == 200
    assert payload['user_stats']['involvement_rate'] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_two_dms(user_1, user_2, user_3, create_dm_2_user, create_dm_3_user):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_3["token"]
    })
    payload = response.json()
    assert response.status_code == 200
    assert payload['user_stats']['involvement_rate'] == 0.5
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_channel_dm(user_1, user_2, public_channel_user1, create_dm_2_user):
    response_1 = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload_1 = response_1.json()

    response_2 = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_2["token"]
    })
    payload_2 = response_2.json()

    assert response_1.status_code == 200
    assert payload_1['user_stats']['involvement_rate'] == 1

    assert response_2.status_code == 200
    assert payload_2['user_stats']['involvement_rate'] == 0.5
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_dm_messages(user_1, send_multiple_dms):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['user_stats']['involvement_rate'] == 1
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_channel_messages(user_1, messages_send_2_channel):
    response = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['user_stats']['involvement_rate'] == 1
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def user_stats_channel_dm_messages(user_1, user_2, user_3, send_multiple_dms, messages_send_2_channel):
    response_1 = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_1["token"]
    })
    payload_1 = response_1.json()

    response_2 = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_2["token"]
    })
    payload_2 = response_2.json()

    response_3 = requests.get(f"{BASE_URL}/user/stats/v1", params={
        "token": user_3["token"]
    })
    payload_3 = response_2.json()

    assert response_1.status_code == 200
    assert payload_1['user_stats']['involvement_rate'] == 1

    assert response_2.status_code == 200
    assert payload_2['user_stats']['involvement_rate'] == 0.3

    assert response_3.status_code == 200
    assert payload_3['user_stats']['involvement_rate'] == 0.1
    requests.delete(f"{BASE_URL}/clear/v1", json={})



def users_stats_none(user_1):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 0
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_one_channel(user_1, public_channel_user1):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 1
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 1
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_two_channels(user_1, user2, public_channel_user1, private_channel_user2):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 1
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 2
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_one_dm(user_1, user2, user3, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 0.7
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 1
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_two_dms(user_1, user_2, user_3, create_dm_2_user, create_dm_3_user):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_3["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 1
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 2
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 0
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_dm_messages(user_1, send_multiple_dms):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 1
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 0
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 2
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 2
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_channel_messages(user_1, messages_send_2_channel):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload['workspace_stats']['utilization_rate'] == 1
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 1
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 0
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 2
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def users_stats_channel_dm_messages(user_1, user_2, user_3, send_multiple_dms, messages_send_2_channel):
    response = requests.get(f"{BASE_URL}/users/stats/v1", params={
        "token": user_1["token"]
    })
    payload = response.json()

    assert payload['workspace_stats']['utilization_rate'] == 1
    assert payload['workspace_stats']['channels_exist'][0]['num_channels_exist'] == 1
    assert payload['workspace_stats']['dms_exist'][0]['num_dms_exist'] == 2
    assert payload['workspace_stats']['messages_exist'][0]['num_messages_exist'] == 4
    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})



def test_valid_img(user_1):
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": user_1["token"],
        "img_url": "valid_url",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100
    })

    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_invalid_img_url(user_1):
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": user_1["token"],
        "img_url": "invalid_url",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_invalid_dimensions(user_1):
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": user_1["token"],
        "img_url": "valid_url",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100000,
        "y_end": 100000
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_invalid_crop(user_1):
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": user_1["token"],
        "img_url": "valid_url",
        "x_start": 100,
        "y_start": 100,
        "x_end": 50,
        "y_end": 50
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_invalid_format(user_1):
    response = requests.post(f"{BASE_URL}/user/profile/uploadphoto/v1", json={
        "token": user_1["token"],
        "img_url": "url_png_image",
        "x_start": 0,
        "y_start": 0,
        "x_end": 100,
        "y_end": 100
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})