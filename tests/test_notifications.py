from distutils.command.config import config
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.message import messages_send_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.helper import SECRET, generate_timestamp
from src.config import port, url
import json
import requests
import urllib
import jwt
import pytest

##MAY CHANGE PORT LATER##
BASE_URL = url


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
def c(user_1, user_2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    return r.json()


@pytest.fixture
def invalid_channel_id():
    return -1


@pytest.fixture
def starting_value():
    return 0


@pytest.fixture
def invalid_starting_value():
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
    return "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Ne"


def test_notifications_invite_to_channel(user_1, user_2, channel_public, message_text):
    # user_1 invites user_2 into channel
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", json={
        "token": user_2['token']
    })
    notifications = request_notifications["notifications"]

    assert notifications[0]["channel_id"] == channel_public['channel_id']
    assert notifications[0]["dm_id"] == -1
    assert notifications[0]["notification_message"] == "mikey invited you to the channel"
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_invite_to_dm(user_1, user_2, c, message_text):
    # user_1 invites user_2 into dm
    # might need a dm_create not sure
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", json={
        "token": user_2['token']
    })
    notifications = request_notifications.json()

    assert notifications[0]["channel_id"] == -1
    assert notifications[0]["dm_id"] == c['dm_id']
    assert notifications[0]["notification_message"] == "mikey invited you to the dm"
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_tag_in_channel(user_1, user_2, channel_public, c, message_text):
    # user_2 joins channel
    requests.post(f"{BASE_URL}/channel/join/v1", json={
        "token": user_2["token"],
        "channel_id": channel_public['channel_id']
    })
    # user_1 tags user_2
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "@miguel hey miguel!"
    })
    # user_2 gets notification
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", json={
        "token": user_2['token']
    })
    notifications = request_notifications.json()

    assert notifications[0]["channel_id"] == channel_public['channel_id']
    assert notifications[0]["dm_id"] == -1
    assert notifications[0]["notification_message"] == "mikey tagged you in a message: @miguel hey miguel!"
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_tag_in_dm(user_1, user_2, channel_public, c, message_text):
    # user_1 tags user_2
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "dm_id": c['dm_id'],
        "message": "@miguel hey miguel!"
    })
    # user_2 gets notification
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", json={
        "token": user_2['token']
    })
    notifications = request_notifications.json()

    assert notifications[0]["channel_id"] == -1
    assert notifications[0]["dm_id"] == c['dm_id']
    assert notifications[0]["notification_message"] == "mikey tagged you in a message: @miguel hey miguel!"
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})

# make notification tests for reacts
#