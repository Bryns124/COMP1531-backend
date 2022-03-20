from distutils.command.config import config
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.other import clear_v1
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
    return requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456",
        "name_first": "Mikey",
        "name_last": "Test"
    })


@pytest.fixture
def user_2():
    return requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "miguel@unsw.com",
        "password": "test123456",
        "name_first": "Miguel",
        "name_last": "Test"
    })


@pytest.fixture
def user_no_access():
    return requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "error@unsw.com",
        "password": "no_access1235667",
        "name_first": "no_access",
        "name_last": "no_access"
    })


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


@pytest.fixture
def channel_private(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Private Channel",
        "is_public": False
    })
    return r.json()


@pytest.fixture
def invalid_channel_id():
    return -1


def test_channel_details_input_error(user_1, invalid_channel_id):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id
    })
    assert r.status_code == InputError.code


def test_channel_details_access_error(user_2, channel_public):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public
    })
    assert r.status_code == AccessError.code


def test_channel_details_wrong_u_id(user_invalid, channel_public):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_invalid['token'],
        "channel_id": channel_public
    })
    assert r.status_code == AccessError.code


def test_channel_details(user_1, channel_public):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public
    })
    data = r.json()
    assert data['channels'] == {
        'name': "Test Channel",
        'is_public': True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
                'name_last': 'Test', 'handle_str': 'migueltest'}
        ]
    }
    assert r.status_code == 200


def test_channel_details_multiple_users(user_1, channel_public, user_2):
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public
    })
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public
    })
    data = r.json()
    assert data['channels'] == {
        'name': "Test Channel",
        'is_public': True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
                'name_last': 'Test', 'handle_str': 'migueltest'}
        ]
    }
    assert r.status_code == 200


def test_channel_join_channel_id_error(user_1, invalid_channel_id):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id
    })
    assert r.status_code == InputError.code


def test_channel_join_already_member_error(user_1, channel_public):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public
    })
    assert r.status_code == InputError.code


def test_channel_join_access_error(user_2, channel_private):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_private
    })
    assert r.status_code == AccessError.code


def test_channel_join_invalid_token(user_invalid, channel_public):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_invalid['token'],
        "channel_id": channel_public
    })
    assert r.status_code == AccessError.code


def test_channel_join(channel_public, user_2):
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public
    })
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public
    })
    data = r.json()
    assert data['channels'] == {
        'name': "Empire Strikes Back",
        'is_public':  True,
        'owner_members': [
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
                'name_last': 'Test', 'handle_str': 'migueltest'}
        ],
        'all_members': [
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
                'name_last': 'Test', 'handle_str': 'migueltest'},
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ]
    }
    assert r.status_code == 200
