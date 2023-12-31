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

"""
Tests for notificatons functions
"""

# Users

@pytest.fixture()
def user_1():
    """
    Fixture for user_1
    """
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456",
        "name_first": "Mikey",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture
def user_2():
    """
    Fixture for user_2
    """
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "miguel@unsw.com",
        "password": "test123456",
        "name_first": "Miguel",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture
def user_3():
    """
    Fixture for user_3
    """
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryan@unsw.com",
        "password": "test123456",
        "name_first": "Bryan",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture
def user_invalid():
    """
    Fixture for user_invalid
    """
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET, algorithm="HS256")


@pytest.fixture
def channel_public(user_1):
    """
    Fixture for public channel
    """
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Test Channel",
        "is_public": True
    })
    return r.json()


@pytest.fixture
def channel_private(user_1):
    """
    Fixture for private channel
    """
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Private Channel",
        "is_public": False
    })
    return r.json()


@pytest.fixture
def c(user_1, user_2):
    """
    Fixture for dm
    """
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    return r.json()


def test_notifications_invalid_token(user_invalid):
    """
    Tests that when the user getting notifications is invalid.
    """
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_invalid
    })
    assert request_notifications.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_invite_to_channel(user_1, user_2, channel_public):
    """
    Tests that when user_1 invites user_2 into the channel, user_2 receives a notification.
    """
    # user_1 invites user_2 into channel
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_2["token"]
    })
    notifications = request_notifications.json()["notifications"]
    assert notifications == [{
        "channel_id": channel_public['channel_id'],
        "dm_id": -1,
        "notification_message": "mikeytest added you to Test Channel"
    }]
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_invite_to_dm(user_2, c):
    """
    Tests that when user_1 invites user_2 into a dm, user_2 receives a notification.
    """
    # user_1 invites user_2 into dm
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_2['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert notifications == [{
        "channel_id": -1,
        "dm_id": c['dm_id'],
        "notification_message": "mikeytest added you to migueltest, mikeytest"
    }]
    # assert notifications[0]["channel_id"] == -1
    # assert notifications[0]["dm_id"] == c['dm_id']
    # assert notifications[0]["notification_message"] == "migueltest added you to Mikey Test"
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_tag_in_channel(user_1, user_2, channel_public):
    """
    Tests that when user_2 tags user_1 in a channel message, user_1 receives a notification.
    """
    # user_2 joins channel
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_public['channel_id']
    })
    # user_2 tags user_1
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "message": "@mikeytest hey mikey!"
    })
    # user_1 gets notification
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]
    assert notifications == [{
        "channel_id": channel_public['channel_id'],
        "dm_id": -1,
        "notification_message": "migueltest tagged you in Test Channel: @mikeytest hey mikey"
    }]
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_tag_in_dm(user_1, user_2, c):
    """
    Tests that when user_2 tags user_1 in a dm message, user_1 receives a notification.
    """
    # user_2 tags user_1
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2['token'],
        "dm_id": c['dm_id'],
        "message": "@mikeytest hey mikey!"
    })
    # user_1 gets notification
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert notifications == [{
        "channel_id": -1,
        "dm_id": c['dm_id'],
        "notification_message": "migueltest tagged you in migueltest, mikeytest: @mikeytest hey mikey"
    }]
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_reacts_in_channel(user_1, user_2, channel_public):
    """
    Tests that when user_2 reacts to a user_1 message in a channel, user_1 receives a notification.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_public['channel_id'],
    })
    message = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "hey miguel!"
    })
    message_info = message.json()["message_id"]

    requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert notifications == [{
        "channel_id": channel_public['channel_id'],
        "dm_id": -1,
        "notification_message": "migueltest reacted to your message in Test Channel"
    }]
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_reacts_in_dm(user_1, user_2, c):
    """
    Tests that when user_2 reacts to a user_1 message in a dm, user_1 receives a notification.
    """
    message = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": c['dm_id'],
        "message": "hey miguel!"
    })
    message_info = message.json()["message_id"]
    requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]
    assert notifications == [{
        "channel_id": -1,
        "dm_id": c['dm_id'],
        "notification_message": "migueltest reacted to your message in migueltest, mikeytest"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_multiple_notifications(user_1, user_2, channel_public):
    """
    Tests that a user can receive and display multiple notifications.
    """
    # user_1 invites user_2 into channel
    inv = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    assert inv.status_code == 200

    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "@migueltest hey miguel!"
    })

    request = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_2['token']
    })
    payload = request.json()["notifications"]

    assert payload == [
        {
            "channel_id": 1,
            "dm_id": -1,
            "notification_message": "mikeytest tagged you in Test Channel: @migueltest hey migu"
        },
        {
            "channel_id": 1,
            "dm_id": -1,
            "notification_message": "mikeytest added you to Test Channel"
        }
    ]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_no_notifications(user_1, user_2, channel_public):
    """
    Tests that a user can receive and display no notifications.
    """
    inv = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    assert inv.status_code == 200
    request_message = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "message": "mikeytest hey mikey!"
    })
    assert request_message.status_code == 200

    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert notifications == []

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_multiple_reacts_for_message_channel(user_1, user_2, user_3, channel_public):
    """
    Tests that a user can display multiple react notifications.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_public['channel_id'],
    })
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_3["token"],
        "channel_id": channel_public['channel_id'],
    })
    message = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "hey guys!"
    })
    message_info = message.json()["message_id"]

    requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })
    requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": user_3["token"],
        "message_id": message_info,
        "react_id": 1
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert notifications == [
        {
        "channel_id": channel_public['channel_id'],
        "dm_id": -1,
        "notification_message": "bryantest reacted to your message in Test Channel"
        },
        {
        "channel_id": channel_public['channel_id'],
        "dm_id": -1,
        "notification_message": "migueltest reacted to your message in Test Channel"
        }]
    assert len(notifications) == 2
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_tag_user_not_in_channel(user_1, user_2, channel_public):
    """
    Tests that a user can be tagged but not receive the notification if the user is not in the channel.
    """
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "@migueltest hey miguel!"
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_2['token']
    })

    notifications = request_notifications.json()["notifications"]

    assert notifications == []

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_unreact_still_notification_channel(user_1, user_2, channel_public):
    """
    Tests that, if a user's message in channel is reacted to then unreacted to, the notification from the react will remain.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_public['channel_id'],
    })
    message = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "hey miguel!"
    })
    message_info = message.json()["message_id"]

    requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })

    requests.post(f"{BASE_URL}/message/unreact/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })

    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert notifications == [{
        "channel_id": channel_public['channel_id'],
        "dm_id": -1,
        "notification_message": "migueltest reacted to your message in Test Channel"
    }]
    assert len(notifications) == 1
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_unreact_still_notification_dm(user_1, user_2, c):
    """
    Tests that, if a user's message in dm is reacted to then unreacted to, the notification from the react will remain.
    """
    message = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": c['dm_id'],
        "message": "hey miguel!"
    })
    message_info = message.json()["message_id"]
    requests.post(f"{BASE_URL}/message/react/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })
    requests.post(f"{BASE_URL}/message/unreact/v1", json={
        "token": user_2["token"],
        "message_id": message_info,
        "react_id": 1
    })
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]
    assert notifications == [{
        "channel_id": -1,
        "dm_id": c['dm_id'],
        "notification_message": "migueltest reacted to your message in migueltest, mikeytest"
    }]
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_notifications_user_more_than_20_notifications(user_1, user_2, channel_public):
    """
    Tests that if a user receives more than 20 notifications, they can only see the most recent 20 notifications.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_public['channel_id'],
    })
    
    for i in range(0, 30):
        requests.post(f"{BASE_URL}/message/send/v1", json={
            "token": user_2['token'],
            "channel_id": channel_public['channel_id'],
            "message": "@mikeytest hey mikey!"
        })
    
    request_notifications = requests.get(f"{BASE_URL}/notifications/get/v1", params={
        "token": user_1['token']
    })
    notifications = request_notifications.json()["notifications"]

    assert len(notifications) == 20

    j = 31
    for i in range(0,20):
        assert notifications[i]["channel_id"] == channel_public['channel_id']
        assert notifications[i]["dm_id"] == -1
        assert notifications[i]["notification_message"] == "migueltest tagged you in Test Channel: @mikeytest hey mikey"
        j -= 1