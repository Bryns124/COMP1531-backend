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


"""Users"""


@pytest.fixture()
def user_1():
    return auth_register_v1("mikey@unsw.com", "test123456", "Mikey", "Test")


@pytest.fixture
def user_2():
    return auth_register_v1("miguel@unsw.com", "test123456", "Miguel", "Test")


@pytest.fixture
def user_no_access():
    return auth_register_v1("error@unsw.com", "no_access1235667", "no_access", "no_access")


@pytest.fixture
def user_invalid():
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET(), algorithm="HS256")


"""Channels"""


@pytest.fixture
def channel_public(user_1):
    return channels_create_v1(user_1["token"], "Test Channel", True)


@pytest.fixture
def channel_private_access(user_no_access):
    return channels_create_v1(user_no_access["token"], "No Access Channel", False)


@pytest.fixture
def channel_private(user_1):
    return channels_create_v1(user_1["token"], "Private Channel", False)


@pytest.fixture
def invalid_channel_id():
    return -1


@pytest.fixture
def starting_value():
    return 0


def test_channel_messages(user_1, channel_public, starting_value):
    r = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        user_1['token'],
        channel_public,
        starting_value
    })
    payload = r.json()
    assert payload 

def test_login():
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "alice@gmail.com",
        "password": "123456"
    })
    payload = r.json()
    assert payload["token"] == "token"  # sample token for now
    assert payload["token"] == 1
