import pytest
import requests
import jwt
from src.other import clear_v1
from src.config import url
from src.helper import SECRET


@pytest.fixture(scope="module")
def clear():
    requests.delete(f"{url}/clear/v1", json={})
    clear_v1()


@pytest.fixture(scope="module")
def user_1():
    r = requests.post(f"{url}/auth/register/v2", json={
        "email": "mikey@unsw.com",
        "password": "test123456",
        "name_first": "Mikey",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture(scope="module")
def user_2():
    r = requests.post(f"{url}/auth/register/v2", json={
        "email": "miguel@unsw.com",
        "password": "test123456",
        "name_first": "Miguel",
        "name_last": "Test"
    })
    return r.json()


@pytest.fixture(scope="module")
def user_no_access():
    r = requests.post(f"{url}/auth/register/v2", json={
        "email": "error@unsw.com",
        "password": "no_access1235667",
        "name_first": "no_access",
        "name_last": "no_access"
    })
    return r.json()


@pytest.fixture(scope="module")
def user_invalid():
    return jwt.encode({'auth_user_id': "invalid", 'session_id': 1}, SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def invalid_user_id():
    return jwt.encode({'auth_user_id': -1, 'session_id': 1}, SECRET, algorithm="HS256")


@pytest.fixture(scope="module")
def invalid_token():
    return "invalid token"


"""Channels"""


@pytest.fixture(scope="module")
def channel_public(user_1):
    r = requests.post(f"{url}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Test Channel",
        "is_public": True
    })
    return r.json()


@pytest.fixture(scope="module")
def channel_private_access(user_no_access):
    r = requests.post(f"{url}/channels/create/v2", json={
        "token": user_no_access['token'],
        "name": "No Access Channel",
        "is_public": False
    })
    return r.json()


@pytest.fixture(scope="module")
def channel_private(user_1):
    r = requests.post(f"{url}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Private Channel",
        "is_public": False
    })
    return r.json()


@pytest.fixture(scope="module")
def invalid_channel_id():
    return -1


@pytest.fixture(scope="module")
def message_text():
    return "Hello world"


@pytest.fixture(scope="module")
def invalid_message_text_short():
    return ""


@pytest.fixture(scope="module")
def invalid_message_text():
    return "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Ne"


def logout_v1(user_token):
    request = requests.post(f"{url}/auth/logout/v1", json={
        "token": user_token
    })
    return request


def test_channel_messages_v2(user_token, channel_id, start):
    request = requests.get(f"{url}/channel/messages/v2", params={
        "token": user_token,
        "channel_id": channel_id,
        "start": start
    })
    return request


def standup_start_v1(user_token, channel_id, length):
    request = requests.post(f"{url}/standup/start/v1", json={
        "token": user_token,
        "channel_id": channel_id,
        "length": length
    })
    return request


def standup_active_v1(user_token, channel_id):
    request = requests.get(f"{url}/standup/active/v1", params={
        "token": user_token,
        "channel_id": channel_id
    })
    return request


def standup_send_v1(user_token, channel_id, message):
    request = requests.post(f"{url}/standup/send/v1", json={
        "token": user_token,
        "channel_id": channel_id,
        "message": message
    })
    return request
