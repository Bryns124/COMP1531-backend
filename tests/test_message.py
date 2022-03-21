from distutils.command.config import config
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.message import messages_send_v1
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
def user_no_access():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "error@unsw.com",
        "password": "no_access1235667",
        "name_first": "no_access",
        "name_last": "no_access"
    })
    return r.json()


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


@pytest.fixture
def starting_value():
    return 0


@pytest.fixture
def invalid_stating_value():
    return 5

# may add fixtures for sending messages


@pytest.fixture
def message_text():
    return "Hello world"


@pytest.fixture
def invalid_message_text_short():
    return ""


@pytest.fixture
def invalid_message_text():
    return "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"


# def test_message_edit(user_1):
#     # craete channel, send message
#     r = requests.put(f"{BASE_URL}/message/edit/v1", json={
#         "token": user_1["token"],
#         "message_id": 1,
#         "message": "user 1 new message"
#     })
#     payload = r.json()
#     assert payload == {}
#     clear_v1()


# def test_channel_message_remove(user_1):
#     # craete channel, send message
#     r = requests.put(f"{BASE_URL}/message/remove/v1", json={
#         "token": user_1["token"],
#         "message_id": 1,
#         "message": "user 2 new message",
#     })
#     payload = r.json()
#     assert payload == {}
#     clear_v1()


# def test_dm_message_edit(user_1):
#     # craete Dm, send message
#     r = requests.put(f"{BASE_URL}/message/edit/v1", json={
#         "token": user_1["token"],
#         "message_id": 1,
#         "message": "user 1 new message"
#     })
#     payload = r.json()
#     assert payload == {}
#     clear_v1()


# def test_dm_message_remove(user_1):
#     # craete Dm, send message
#     r = requests.put(f"{BASE_URL}/message/remove/v1", json={
#         "token": user_1["token"],
#         "message_id": 1,
#         "message": "user 2 new message",
#     })
#     payload = r.json()
#     assert payload == {}
#     clear_v1()


def test_channel_messages(user_1, channel_public, starting_value, message_text):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    r = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    payload = r.json()
    assert r.status_code == 200
    assert payload['messages']['message_id'] == 1
    assert payload['messages']['u_id'] == 1
    assert payload['messages']['message'] == message_text
    assert payload['start'] == 0
    assert payload['end'] == -1
    # {"messages": [
    #     {
    #         'message_id': 1,
    #         'u_id': 1,
    #         'message': "Hello world",
    #         'time_created': 1582426789,
    #     },
    # ],
    #     'start': 0,
    #     'end': -1,
    # }


def test_channel_messages_channel_id_error(user_1, invalid_channel_id, invalid_starting_value):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    r = requests.post(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "start": invalid_starting_value
    })
    assert r.status_code == InputError.code


def test_channel_messages_unauthorised_user(channel_public, user_2, starting_value):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    r = requests.post(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public,
        "start": starting_value
    })
    assert r.status_code == AccessError.code


def test_messages_send(user_1, channel_public, message_text, starting_value):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    payload = request.json()
    assert channel_messages_v1(user_1['token'], channel_public, starting_value)[
        'messages'][-1]['message_id'] == payload["message_id"]


def test_messges_send_channel_id_error(user_1, invalid_channel_id, message_text):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "message": message_text
    })

    assert request.status_code == InputError.code


def test_messages_send_message_lengthlong_error(user_1, channel_public, invalid_message_text):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": invalid_message_text
    })

    assert request.status_code == InputError.code


def test_messages_send_message_lengthshort_error(user_1, channel_public, invalid_message_text_short):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })

    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": invalid_message_text_short
    })

    assert request.status_code == InputError.code


def test_messages_send_access_error(user_2, channel_public, message_text):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })

    assert request.status_code == AccessError.code


def test_messages_send_token_error(user_invalid, channel_public, message_text):
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_invalid['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    assert request.status_code == AccessError.code
