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
    return  requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "miguel@unsw.com",
        "password": "test123456",
        "name_first": "Miguel",
        "name_last": "Test"
    })



@pytest.fixture
def user_no_access():
    return  requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "error@unsw.com",
        "password": "no_access1235667",
        "name_first": "no_access",
        "name_last": "no_access"
    })


@pytest.fixture
def user_invalid():
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET, algorithm="HS256")

