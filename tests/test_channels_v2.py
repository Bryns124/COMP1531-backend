import pytest
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.helper import SECRET
from src.config import port
import json
from flask import request, Flask
import jwt
import pytest
import requests

BASE_URL = f"http://127.0.0.1:{port}/"


@pytest.fixture
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


@pytest.fixture  # user1 creates a public channel
def private_second_channel_user1(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "User_1_Private",
        "is_public": False
    })
    return r.json()


def test_listall_no_channel(user_1):
    """
    test for if no channels have been created
    """
    response = requests.get(f"{BASE_URL}/channels/listall/v2", json={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload["channels"] == []
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_listall_public(user_1, public_channel_user1):
    """
    test for listing public channels
    """
    response = requests.get(f"{BASE_URL}/channels/listall/v2", json={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload["channels"] == [{
        "channel_id": public_channel_user1["channel_id"],
        "name": "Public"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_listall_private(user_1, private_channel_user2):
    """
    test for listing private channel
    """
    response = requests.get(f"{BASE_URL}/channels/listall/v2", json={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload["channels"] == [{
        "channel_id": private_channel_user2["channel_id"],
        "name": "Private"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_listall_both(user_1, user_2, public_channel_user1, private_channel_user2):
    """
    test if two channels are created by separate users
    """
    response = requests.get(f"{BASE_URL}/channels/listall/v2", json={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload["channels"] == [
        {
            "channel_id": public_channel_user1["channel_id"],
            "name": "Public"
        },
        {
            "channel_id": private_channel_user2["channel_id"],
            "name": "Private"
        }
    ]

    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_create_public_channel(user_1):
    """
    Test to check if creating a new public channel return the channel-id of that channel
    Assumption: The token is correct
    """
    response = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "public_channel",
        "is_public": True
    })
    payload = response.json()
    assert payload["channel_id"] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_create_private_channel(user_1):
    """
    Test to check if creating a new private channel will return the correct channel_id
    Assumption: The token is correct
    """
    response = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "test_channel",
        "is_public": False
    })
    payload = response.json()
    assert payload["channel_id"] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_create_channel_invalid_name_1(user_1):
    """
    Test to check if creating a channel with an invalid name of less than 1 character raises an Input Error
    Assumption: The token is correct
    """
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "",
        "is_public": True
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_create_channel_invalid_name_2(user_1):
    """
    Test to check if creating a new channel with an invalid name of more than 20 characters raises an Input Error
    Assumption: The token is correct
    """
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "abcdefghijklmnopqrstuv",
        "is_public": True
    })

    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_create_multiple_channel(user_1):
    """
    Test to check if creating multiple channels will return sequential channel_ids
    Assumption: the channels will not be sorted by their name in alphabetical order
    """
    response1 = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "channel_1",
        "is_public": True
    })
    payload1 = response1.json()
    assert payload1["channel_id"] == 1

    response2 = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1["token"],
        "name": "channel_2",
        "is_public": True
    })
    payload2 = response2.json()
    assert payload2["channel_id"] == 2
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_list_private(user_2, private_channel_user2):
    """
    Test to check if a member of a private channel can list all the channels he is a member of
    Assumption: The token is correct
    Assumption: The user is only a member of one channel
    """
    response = requests.get(f"{BASE_URL}/channels/list/v2", json={
        "token": user_2["token"]
    })
    payload = response.json()
    assert payload["channels"] == [
        {
            "channel_id": private_channel_user2["channel_id"],
            "name": "Private",
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_list_public(user_1, public_channel_user1):
    """
    Test to check if a member of a public channel can list all the channels he is a member of
    Assumption: The token is correct
    Assumption: The user is only a member of one channel
    """
    response = requests.get(f"{BASE_URL}/channels/list/v2", json={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload["channels"] == [
        {
            "channel_id": public_channel_user1["channel_id"],
            "name": "Public"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_list_empty(user_2):
    """
    Test to check if an empty list of dictionaries is returned if the user is not a member of any channels
    Assumption: The token is correct
    """
    response = requests.get(f"{BASE_URL}/channels/list/v2", json={
        "token": user_2["token"]
    })
    payload = response.json()
    assert payload["channels"] == []
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_list_multiple_created(user_1, public_channel_user1, private_second_channel_user1):
    """
    Test to check if a list of dictionaries containing channel details is correctly generated,
    when the user creates and is the owner of multiple channels
    Assumption: The token is correct
    """
    response = requests.get(f"{BASE_URL}/channels/list/v2", json={
        "token": user_1["token"]
    })
    payload = response.json()
    assert payload["channels"] == [
        {
            "channel_id": public_channel_user1["channel_id"],
            "name": "Public",
        },
        {
            "channel_id": private_second_channel_user1["channel_id"],
            "name": "User_1_Private",
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
