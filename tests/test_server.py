import pytest
import json
import requests
import urllib

##MAY CHANGE PORT LATER##
BASE_URL = "http://127.0.0.1:5000/"


def test_register():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "alice@gmail.com",
        "password": "123456",
        "name_first": "Alice",
        "name_last": "Wan"
    })
    payload = r.json()
    assert payload["token"] == "token"  # sample token for now
    assert payload["auth_user_id"] == 1


def test_login():
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "alice@gmail.com",
        "password": "123456"
    })
    payload = r.json()
    assert payload["token"] == "token"  # sample token for now
    assert payload["token"] == 1


def test_channel_create():
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        # "token" : (token), #whitebox test
        "name": "Alice public channel",
        "is_public": True
    })
    payload = r.json()
    assert payload["channel_"] == 1


if __name__ == "__main__":
    test_simple()
