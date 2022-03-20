from re import T
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
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
def channel_public(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Test Channel",
        "is_public": True
    })
    return r.json()


@pytest.fixture
def message_send(user_1, channel_public):
    r = requests.post(f"{BASE_URL}/messages/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public,
        "message": "Hello world"
    })
    return r.json()


@pytest.fixture
def DM(user_1):
    return requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_1['auth_user_id']]
    })


def test_clear_empty():
    r = requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    body = r.json()
    assert body == {}
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_clear_user(user_1, user_2):
    r = requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    body = r.json()
    assert body == {}
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_clear_channel(user_1, user_2, channel_public, channel_private):
    r = requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    body = r.json()
    assert body == {}
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_clear_messages(channel_public, message_send):
    r = requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    body = r.json()
    assert body == {}
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_clear_DM(DM):
    r = requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    body = r.json()
    assert body() == {}
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
