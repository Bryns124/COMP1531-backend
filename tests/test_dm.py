import pytest
from src.dm import dm_create_v1, dm_list_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.auth import auth_register_v1
from src.other import clear_v1
from src.error import AccessError, InputError
from src.helper import SECRET
from src.config import port
import json
from flask import Flask
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
    r = requests.post(f"{BASE_URL}/auth/register/v2", json = {
        "email": "michael@gmail.com",
        "password": "1234567788",
        "name_first": "Michael",
        "name_last": "Chai"
    })
    return r.json

@pytest.fixture
def create_dm_2_user(user1, user2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": user1['token'],
        "u_ids": [int(user2["auth_user_id"])]
    })
    return r.json()


@pytest.fixture
def create_dm_3_user(user1, user2, user3):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": user1['token'],
        "u_ids": [int(user2["auth_user_id"]), int(user3["auth_user_id"])]
    })
    return r.json()



def test_dm_create_2_users(user1, user2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids": [int(user2('auth_user_id'))]
    })
    payload = r.json()
    assert payload['dm_id'] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_3_users(user1, user2, user3):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1("token"),
        "u_ids": [int(user2["auth_user_id"]), int(user3["auth_user_id"])]
    })
    payload = r.json()
    assert payload['dm_id'] == 1
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_2_dms(user1, user2, user3, user4):
    response_1 = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1("token"),
        "u_ids": [int(user2('auth_user_id'))]
    })

    response_2 = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user3("token"),
        "u_ids": [int(user4('auth_user_id'))]
    })
    payload_1 = response_1.json()
    payload_2 = response_2.json()
    assert payload_1['dm_id'] == 1
    assert payload_2['dm_id'] == 2
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_invalid_ids(user1):
    invalid_id = 200
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids": [invalid_id]
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_create_duplicate_ids_1(user1):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1('token'),
        "u_ids": [int(user1('auth_user_id'))]
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_create_duplicate_ids_2(user1, user2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user1("token"),
        "u_ids": [int(user2('auth_user_id')), int(user2('auth_user_id'))]
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_list_empty(user1):
    r = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user1("token")
    })

    payload = r.json()
    assert payload == []
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_list_two_users(user1, user2, create_dm_2_user):
    response_1 = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user1("token")
    })

    response_2 = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user2("token")
    })

    payload_1 = response_1.json()
    payload_2 = response_2.json()
    assert payload_1["dms"] == [
        {
            "dm_id" : 1,
            "name" : "adiyatrahman, alicewan"
        }
    ]
   assert payload_1["dms"] == [
        {
            "dm_id" : 1,
            "name" : "adiyatrahman, alicewan",
        }
    ]
    # assert payload_1 == [{
    #         'DM_id' : 1,
    #         'name' : "adiyatrahman, alicewan",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user2["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # }]

    # assert payload_2 == [{
    #         'DM_id' : 1,
    #         'name' : "adiyatrahman, alicewan",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user2["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_list_three_users(user1, user2, user3, create_dm_3_user):
    response_1 = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user1("token")
    })

    response_2 = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user2("token")
    })

    response_3 = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user3("token")
    })

    payload_1 = response_1.json()
    payload_2 = response_2.json()
    payload_3 = response_3.json()

   assert payload_1["dms"] == [
        {
            "dm_id" : 1,
            "name" : "adiyatrahman, alicewan, michaelchai"
        }
    ]

   assert payload_2["dms"] == [
        {
            "dm_id" : 1,
            "name" : "adiyatrahman, alicewan, michaelchai"
        }
    ]

   assert payload_3["dms"] == [
        {
            "dm_id" : 1,
            "name" : "adiyatrahman, alicewan, michaelchai"
        }
    ]
    # assert payload_1 == [{
    #         'DM_id' : 1,
    #         'name' : "adiyatrahman, alicewan, michaelchai",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user2["auth_user_id"], user3["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # }]

    # assert payload_2 == [{
    #         'DM_id' : 1,
    #         'name' : "adiyatrahman, alicewan, michaelchai",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user2["auth_user_id"], user3["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # }]

    # assert payload_3 == [{
    #         'DM_id' : 1,
    #         'name' : "adiyatrahman, alicewan, michaelchai",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user2["auth_user_id"], user3["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_list_two_dms(user1, user2, user3):
    response_1 = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": user1['token'],
        "u_ids": [int(user2["auth_user_id"])]
    })

    response_2 = requests.post(f"{BASE_URL}/dm/create/v1", json = {
        "token": user1['token'],
        "u_ids": [int(user3["auth_user_id"])]
    })

    response_3 = requests.get(f"{BASE_URL}/dm/list/v1", json = {
        "token": user1("token")
    })

    payload = response_3.json()

   assert payload["dms"] == [
        {
            "dm_id" : 1,
            "name" : "adiyatrahman, alicewan"
        },
        {
            "dm_id" : 2,
            'name' : "adiyatrahman, michaelchai",
        }
    ]

    # assert payload == [{
    #         'DM_id' : 1,
    #         'name' : "adiyatrahman, alicewan",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user2["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # },
    # {
    #         'DM_id' : 2,
    #         'name' : "adiyatrahman, michaelchai",
    #         'owner_members' : [user1["auth_user_id"]], #check again if this is leagal
    #         'all_members' : [user1["auth_user_id"], user3["auth_user_id"]],
    #         'messages_list': [], #list of message IDs
    #         'start': 25,
    #         'end': 75,
    # }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_remove(user1, user2, user3, create_dm_3_user):
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": user1["token"],
        "DM_id": 1
    })

    assert response.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_remove_invalid_id(user1, user2, user3, create_dm_3_user):
    invalid_id = 200
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": user1["token"],
        "DM_id": 200
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_remove_not_creator(user1, user2, user3, create_dm_3_user):
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": user2["token"],
        "DM_id": 1
    })

    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_remove_not_member(user1, user2, user3, create_dm_3_user):
    requests.post(f"{BASE_URL}/dm/leave/v1", json = {
        "token": user1["token"],
        "DM_id": 1
    })

    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json = {
        "token": user1["token"],
        "DM_id": 1
    })

    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_details_invalid_dm_id(user_1):
    response = requests.get(f"{BASE_URL}/dm/details/v1", json = {
        "token": user1["token"],
        "DM_id": 1
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_details_no_access(user_3, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/dm/details/v1", json = {
        "token": user_3["token"],
        "DM_id": 1
    })
    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_dm_details_3_users(create_dm_3_user):
    response = requests.get(f"{BASE_URL}/dm/details/v1", json = {
        "token": user_3["token"],
        "DM_id": 1
    })
    payload = response.json()
    assert payload["name"] == "adiyatrahman, alicewan, michaelchai"
    assert payload["members"] == [
        int(user2["auth_user_id"]),
        int(user2["auth_user_id"]),
        int(user3["auth_user_id"])
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})