import pytest
import src.server
from src.error import AccessError, InputError
from src.helper import SECRET, generate_timestamp, decode_token
from src.config import port, url
import json
from flask import Flask
import requests
import urllib
import jwt
import pytest

BASE_URL = url
requests.delete(f"{BASE_URL}/clear/v1", json={})

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
def starting_value():
    return 0


@pytest.fixture
def invalid_message_text():
    return "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Ne"


# requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_invalid_ids(user_1):
    invalid_id = 200
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [invalid_id]
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_duplicate_ids_1(user_1):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_1['auth_user_id']]
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_duplicate_ids_2(user_1, user_2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id'], user_2['auth_user_id']]
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_2_users(user_1, user_2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2["auth_user_id"]]
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload['dm_id'] == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_create_3_users(user_1, user_2, user_3):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1["token"],
        "u_ids": [user_2["auth_user_id"], user_3['auth_user_id']]
    })
    payload = r.json()
    assert payload['dm_id'] == 1
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_list_empty(user_1):
    r = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })

    assert r.status_code == 200
    payload = r.json()
    assert payload["dms"] == []
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_list_two_users(user_1, user_2, create_dm_2_user):
    response_1 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })

    response_2 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_2["token"]
    })

    assert response_1.status_code == 200
    assert response_2.status_code == 200
    payload_1 = response_1.json()
    payload_2 = response_2.json()
    assert payload_1["dms"] == [
        {
            "dm_id": 1,
            "name": "adiyatrahman, alicewan"
        }
    ]
    assert payload_2["dms"] == [
        {
            "dm_id": 1,
            "name": "adiyatrahman, alicewan",
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_list_three_users(user_1, user_2, user_3, create_dm_3_user):
    response_1 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })

    response_2 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_2["token"]
    })

    response_3 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_3["token"]
    })

    payload_1 = response_1.json()
    payload_2 = response_2.json()
    payload_3 = response_3.json()

    assert payload_1["dms"] == [
        {
            "dm_id": 1,
            "name": "adiyatrahman, alicewan, michaelchai"
        }
    ]

    assert payload_2["dms"] == [
        {
            "dm_id": 1,
            "name": "adiyatrahman, alicewan, michaelchai"
        }
    ]

    assert payload_3["dms"] == [
        {
            "dm_id": 1,
            "name": "adiyatrahman, alicewan, michaelchai"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_list_two_dms(user_1, user_2, user_3):
    requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })

    requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_3['auth_user_id']]
    })

    response_3 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })

    payload = response_3.json()

    assert payload["dms"] == [
        {
            "dm_id": 1,
            "name": "adiyatrahman, alicewan"
        },
        {
            "dm_id": 2,
            'name': "alicewan, michaelchai",
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_remove_invalid_id(user_1, user_2, user_3, create_dm_3_user):
    invalid_id = 200
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json={
        "token": user_1["token"],
        "dm_id": invalid_id
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_remove_not_creator(user_1, user_2, user_3, create_dm_3_user):
    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json={
        "token": user_2["token"],
        "dm_id": 1
    })

    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_remove_not_member(user_1, user_2, user_3, create_dm_3_user):
    requests.post(f"{BASE_URL}/dm/leave/v1", json={
        "token": user_1["token"],
        "dm_id": 1
    })

    response = requests.delete(f"{BASE_URL}/dm/remove/v1", json={
        "token": user_1["token"],
        "dm_id": 1
    })

    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_remove(user_1, user_2, user_3, create_dm_3_user):
    response1 = requests.delete(f"{BASE_URL}/dm/remove/v1", json={
        "token": user_1["token"],
        "dm_id": 1
    })

    payload1 = response1.json()
    assert payload1 == {}

    response2 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })
    payload2 = response2.json()
    assert payload2["dms"] == []
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_details_invalid_dm_id(user_1):
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={
        "token": user_1["token"],
        "dm_id": 1
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_details_no_access(user_3, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={
        "token": user_3["token"],
        "dm_id": 1
    })
    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_details_3_users(user_1, user_2, user_3, create_dm_3_user):
    response = requests.get(f"{BASE_URL}/dm/details/v1", params={
        "token": user_3["token"],
        "dm_id": 1
    })
    payload = response.json()
    assert payload["name"] == "adiyatrahman, alicewan, michaelchai"
    assert payload["members"] == [
        {'u_id': 1, 'email': 'alice@gmail.com', 'name_first': 'Alice',
         'name_last': 'Wan', 'handle_str': 'alicewan', "profile_img_url": "{BASE_URL}/static/default.jpg"},
        {'u_id': 2, 'email': 'adi@gmail.com', 'name_first': 'Adiyat',
            'name_last': 'Rahman', 'handle_str': 'adiyatrahman', "profile_img_url": "{BASE_URL}/static/default.jpg"},
        {'u_id': 3, 'email': 'michael@gmail.com', 'name_first': 'Michael',
            'name_last': 'Chai', 'handle_str': 'michaelchai', "profile_img_url": "{BASE_URL}/static/default.jpg"}
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_leave_invalid_dm_id(user_1):
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json={
        "token": user_1["token"],
        "dm_id": 1
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_leave_no_access(user_3, create_dm_2_user):
    response = requests.post(f"{BASE_URL}/dm/leave/v1", json={
        "token": user_3["token"],
        "dm_id": 1
    })
    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_leave(user_1, create_dm_2_user):
    response1 = requests.post(f"{BASE_URL}/dm/leave/v1", json={
        "token": user_1["token"],
        "dm_id": 1
    })
    payload1 = response1.json()

    response2 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })
    payload2 = response2.json()

    assert payload1 == {}
    assert payload2["dms"] == []
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_leave_multiple_dms(user_1, create_dm_3_user, create_dm_2_user):
    response1 = requests.post(f"{BASE_URL}/dm/leave/v1", json={
        "token": user_1["token"],
        "dm_id": 2
    })
    payload1 = response1.json()
    response2 = requests.get(f"{BASE_URL}/dm/list/v1", params={
        "token": user_1['token']
    })
    payload2 = response2.json()
    assert response1.status_code == 200
    assert payload1 == {}
    assert payload2["dms"] == [{
        'dm_id': 1,
        'name': "adiyatrahman, alicewan, michaelchai"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_send_no_dm(user_1):
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 100,
        "message": "hello world"
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_send_invalid_message(user_1, create_dm_2_user):
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Ne"
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_send_access_error_1(user_3, create_dm_2_user):
    response = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_3['token'],
        "dm_id": 1,
        "message": "hello world"
    })

    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_send_multiple_dms(user_1, create_dm_3_user, create_dm_2_user):
    response1 = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 2,
        "message": "hello"
    })

    response2 = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 2,
        "message": "world"
    })

    payload_1 = response1.json()
    payload_2 = response2.json()
    assert payload_1["message_id"] == 1
    assert payload_2["message_id"] == 2
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_input_error(user_1):
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1["token"],
        "dm_id": 1,
        "start": 0
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_incorrect_start(user_1, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1["token"],
        "dm_id": 1,
        "start": 100
    })
    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_no_acces(user_3, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_3["token"],
        "dm_id": 1,
        "start": 0
    })
    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages(user_1, create_dm_2_user):
    time_sent = generate_timestamp()
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1["token"],
        "dm_id": 1,
        "message": "hello world"
    })
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1["token"],
        "dm_id": 1,
        "start": 0
    })
    payload = response.json()
    assert payload["messages"][-1]["message_id"] == 1
    assert payload["messages"][-1]["u_id"] == 1
    assert payload["messages"][-1]["message"] == "hello world"
    assert payload["messages"][-1]['time_sent'] >= time_sent
    assert payload["start"] == 0
    assert payload["end"] == -1

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_none(user_1, create_dm_2_user):
    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1["token"],
        "dm_id": 1,
        "start": 0
    })
    payload = response.json()
    assert payload["messages"] == []
    assert payload["start"] == 0
    assert payload["end"] == -1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_multiple(user_1, create_dm_2_user, starting_value):
    time_sent = generate_timestamp()
    for _ in range(50):
        requests.post(f"{BASE_URL}/message/senddm/v1", json={
            "token": user_1["token"],
            "dm_id": 1,
            "message": "hello world"
        })

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1['token'],
        "dm_id": 1,
        "start": 0
    })

    payload = response.json()
    for i in range(49):
        assert response.status_code == 200
        assert payload['messages'][i]['message_id'] == (
            starting_value + 50) - i
        assert payload['messages'][i]['u_id'] == 1
        assert payload['messages'][i]['message'] == "hello world"
        assert payload['messages'][i]['time_sent'] >= time_sent
        assert payload['start'] == 0
        assert payload['end'] == 50
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_messages_multiple_51(user_1, create_dm_2_user, starting_value):
    time_sent = generate_timestamp()
    for _ in range(51):
        requests.post(f"{BASE_URL}/message/senddm/v1", json={
            "token": user_1["token"],
            "dm_id": 1,
            "message": "hello world"
        })

    response = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1['token'],
        "dm_id": 1,
        "start": 0
    })

    payload = response.json()
    for i in range(49):
        assert response.status_code == 200
        assert payload['messages'][i]['message_id'] == (
            starting_value + 51) - i
        assert payload['messages'][i]['u_id'] == 1
        assert payload['messages'][i]['message'] == "hello world"
        assert payload['messages'][i]['time_sent'] >= time_sent
        assert payload['start'] == 0
        assert payload['end'] == 50
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_edit_invalid_message(user_1, create_dm_2_user, invalid_message_text):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "hello world"
    })

    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": invalid_message_text
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_edit_invalid_mid(user_1, create_dm_2_user):
    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "user 1 new message"
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_edit_no_access(user_1, user_2, create_dm_2_user):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "hello world"
    })

    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_2["token"],
        "message_id": 1,
        "message": "no access"
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_message_edit1(user_1,create_dm_2_user):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "hello world"
    })

    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "new message"
    })
    payload = r.json()
    assert payload == {}

    r2 = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1['token'],
        "dm_id": 1,
        "start": 0
    })
    assert r2.status_code == 200
    payload = r2.json()
    assert payload["messages"][-1]["message"] == "new message"
    requests.delete(f"{BASE_URL}/clear/v1", json={})

def test_message_edit2(user_1, user_3, create_dm_3_user):
    re = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_3['token'],
        "dm_id": 1,
        "message": "hello world"
    })
    assert re.status_code == 200
    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "new message"
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload == {}

    r2 = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1['token'],
        "dm_id": 1,
        "start": 0
    })
    assert r2.status_code == 200
    payload = r2.json()
    assert payload["messages"][-1]["message"] == "new message"
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_remove_invalid_mid(user_1, create_dm_2_user):
    r = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user_1["token"],
        "message_id": 1,
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_remove_no_access(user_1, user_2, create_dm_2_user):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "hello world"
    })

    r = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user_2["token"],
        "message_id": 1,
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_remove1(user_1, user_2, create_dm_2_user):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "hello"
    })
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "world"
    })
    r = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user_1["token"],
        "message_id": 2,
    })
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1['token'],
        "dm_id": 1,
        "start": 0
    })
    assert r2.status_code == 200
    payload = r2.json()
    assert payload["messages"][-1]["message"] == "hello"
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_remove2(user_1, user_2, create_dm_3_user):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2['token'],
        "dm_id": 1,
        "message": "hello"
    })
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2['token'],
        "dm_id": 1,
        "message": "world"
    })
    r = requests.delete(f"{BASE_URL}/message/remove/v1", json={
        "token": user_1["token"],
        "message_id": 2,

    })
    assert r.status_code == 200
    r2 = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1['token'],
        "dm_id": 1,
        "start": 0
    })
    assert r2.status_code == 200
    payload = r2.json()
    assert payload["messages"][-1]["message"] == "hello"
    requests.delete(f"{BASE_URL}/clear/v1", json={})
