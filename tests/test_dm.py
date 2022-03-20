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
