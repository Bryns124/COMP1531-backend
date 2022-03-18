from distutils.command.config import config
from turtle import clear
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
    return auth_register_v1("mikey@unsw.com", "test123456", "Mikey", "Test")


@pytest.fixture
def user_2():
    return auth_register_v1("miguel@unsw.com", "test123456", "Miguel", "Test")


@pytest.fixture
def user_no_access():
    return auth_register_v1("error@unsw.com", "no_access1235667", "no_access", "no_access")


@pytest.fixture
def user_invalid():
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET, algorithm="HS256")


# Channels


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

# may add fixtures for sending messages


def test_message_edit(user_1):
    # craete channel, send message
    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "user 1 new message"
    })
    payload = r.json()
    assert payload == {}
    clear_v1()


def test_channel_message_remove(user_1):
    # craete channel, send message
    r = requests.put(f"{BASE_URL}/message/remove/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "user 2 new message",
    })
    payload = r.json()
    assert payload == {}
    clear_v1()


def test_dm_message_edit(user_1):
    # craete Dm, send message
    r = requests.put(f"{BASE_URL}/message/edit/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "user 1 new message"
    })
    payload = r.json()
    assert payload == {}
    clear_v1()


def test_dm_message_remove(user_1):
    # craete Dm, send message
    r = requests.put(f"{BASE_URL}/message/remove/v1", json={
        "token": user_1["token"],
        "message_id": 1,
        "message": "user 2 new message",
    })
    payload = r.json()
    assert payload == {}
    clear_v1()


@pytest.fixture
def message_text():
    return "Hello world"


def invalid_message_text():
    return "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"


def test_channel_messages(user_1, channel_public, starting_value, message_text):
    messages_send_v1(user_1['token'], channel_public, message_text)
    r = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public,
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
    clear_v1()


def test_channel_messages_channel_id_error():
    pass


def test_messages_send(user_1, channel_public, message_text, starting_value):
    r = requests.get(f"{BASE_URL}/messages/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public,
        "message": message_text
    })
    payload = r.json()
    assert payload['message_id'] == channel_messages_v1(
        user_1['token'], channel_public, starting_value)['messages'][-1]['message_id']
    clear_v1()


def test_messges_send_channel_id_error(user_1, invalid_channel_id, message_text):
    r = requests.get(f"{BASE_URL}/messages/send/v1", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "message": message_text
    })

    assert r.status_code == InputError.code
    clear_v1()


def test_messages_send_message_length_error(user_1, channel_public, invalid_message_text):
    r = requests.get(f"{BASE_URL}/messages/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public,
        "message": invalid_message_text
    })

    assert r.status_code == InputError.code
    clear_v1()


def test_messages_send_access_error(user_2, channel_public, message_text):
    r = requests.get(f"{BASE_URL}/messages/send/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public,
        "message": message_text
    })

    assert r.status_code == AccessError.code
    clear_v1()


def test_messages_send_token_error(user_invalid, channel_public, message_text):
    r = requests.get(f"{BASE_URL}/messages/send/v1", json={
        "token": user_invalid['token'],
        "channel_id": channel_public,
        "message": message_text
    })
    assert r.status_code == AccessError.code
    clear_v1()


def test_login():
    r = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": "alice@gmail.com",
        "password": "123456"
    })
    payload = r.json()
    assert payload["token"] == "token"  # sample token for now
    assert payload["token"] == 1
