from distutils.command.config import config
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.message import messages_send_v1, message_pin_v1, message_unpin_v1
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
requests.delete(f"{BASE_URL}/clear/v1", json={})

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
def user_3():
    r = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "ali@unsw.com",
        "password": "123456789",
        "name_first": "Alice",
        "name_last": "Wan"
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
def create_dm_2_user(user_1, user_2):
    r = requests.post(f"{BASE_URL}/dm/create/v1", json={
        "token": user_1['token'],
        "u_ids": [user_2['auth_user_id']]
    })
    return r.json()


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
def create_dm_2_user(user_1, user_2):
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


@pytest.fixture
def invalid_message_id():
    return -1


@pytest.fixture
def invalid_react_id():
    return -1
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
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    payload = r.json()
    assert r.status_code == 200
    assert payload['messages'][-1]['message_id'] == 1
    assert payload['messages'][-1]['u_id'] == 1
    assert payload['messages'][-1]['message'] == message_text
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
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_messages_channel_id_error(user_1, invalid_channel_id, invalid_starting_value):
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "start": invalid_starting_value
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_messages_starting_value_error(user_1, channel_public, invalid_starting_value):
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": invalid_starting_value
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_messages_unauthorised_user(channel_public, user_2, starting_value):
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_2(user_1, channel_public, message_text, starting_value):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })

    payload = request.json()
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    body = r.json()
    assert body['messages'][-1]['message_id'] == payload["message_id"]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_multiple_channels(user_1, channel_private, channel_public, message_text, starting_value):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })

    payload = request.json()
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    body = r.json()
    assert body['messages'][-1]['message_id'] == payload["message_id"]
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messges_send_channel_id_error(user_1, invalid_channel_id, message_text):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "message": message_text
    })

    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_message_lengthlong_error(user_1, channel_public, invalid_message_text):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": invalid_message_text
    })

    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_message_lengthshort_error(user_1, channel_public, invalid_message_text_short):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": invalid_message_text_short
    })
    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_access_error(user_2, channel_public, message_text):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })

    assert request.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_token_error(user_invalid, channel_public, message_text):
    request = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_invalid,
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    assert request.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_50(user_1, channel_public, message_text, starting_value):
    time_sent = generate_timestamp()
    for _ in range(50):
        requests.post(f"{BASE_URL}/message/send/v1", json={
            "token": user_1['token'],
            "channel_id": channel_public['channel_id'],
            "message": message_text
        })

    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    payload = r.json()
    for i in range(49):
        assert r.status_code == 200
        assert payload['messages'][i]['message_id'] == (
            starting_value + 50) - i
        assert payload['messages'][i]['u_id'] == 1
        assert payload['messages'][i]['message'] == message_text
        assert payload['messages'][i]['time_sent'] >= time_sent
        assert payload['start'] == 0
        assert payload['end'] == 50
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_messages_send_51(user_1, channel_public, message_text, starting_value):
    time_sent = generate_timestamp()
    for _ in range(50):
        requests.post(f"{BASE_URL}/message/send/v1", json={
            "token": user_1['token'],
            "channel_id": channel_public['channel_id'],
            "message": message_text
        })

    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": starting_value
    })
    payload = r.json()
    for i in range(49):
        assert r.status_code == 200
        assert payload['messages'][i]['message_id'] == (
            starting_value + 50) - i
        assert payload['messages'][i]['u_id'] == 1
        assert payload['messages'][i]['message'] == message_text
        assert payload['messages'][i]['time_sent'] >= time_sent
        assert payload['start'] == 0
        assert payload['end'] == 50
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_search_too_short(user_1, invalid_message_text_short):
    r = requests.get(f"{BASE_URL}/search/v1", params={
        "token": user_1['token'],
        "query_str": invalid_message_text_short
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_search_too_long(user_1, invalid_message_text):
    r = requests.get(f"{BASE_URL}/search/v1", params={
        "token": user_1['token'],
        "query_str": invalid_message_text
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_search_specific(user_1, user_2, channel_public):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "find this"
    })
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "not this"
    })
    r = requests.get(f"{BASE_URL}/search/v1", params={
        "token": user_2['token'],
        "query_str": "find this"
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload["messages"][-1]["u_id"] == 1
    assert payload["messages"][-1]["message"] == "find this"
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_search_multiple(user_1, user_2, create_dm_2_user, channel_public):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "we are looking for birdsarereal"
    })
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "I believe birdsarereal blah blah"
    })
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2['token'],
        "dm_id": 1,
        "message": "birdsarentreal dont find me"
    })
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2['token'],
        "dm_id": 1,
        "message": "imhidingbirdsarerealoverhere"
    })
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "Like i said,birdsarereal"
    })
    r = requests.get(f"{BASE_URL}/search/v1", params={
        "token": user_2['token'],
        "query_str": "birdsarereal"
    })
    assert r.status_code == 200
    payload = r.json()
    assert payload["messages"][0]["message"] == "we are looking for birdsarereal"
    assert payload["messages"][1]["message"] == "I believe birdsarereal blah blah"
    assert payload["messages"][2]["message"] == "imhidingbirdsarerealoverhere"
    assert payload["messages"][3]["message"] == "Like i said,birdsarereal"
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_messages_share_invalid_channeldm(user_1):
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_1["token"],
        "og_message_id": 1,
        "message": "new message",
        "channel_id": -20,
        "dm_id": 500
    })
    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_messages_share_no_minus1(user_1, user_2, channel_public, create_dm_2_user):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "Hello world"
    })
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_1["token"],
        "og_message_id": 1,
        "message": "new message",
        "channel_id": channel_public['channel_id'],
        "dm_id": create_dm_2_user['dm_id']
    })
    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


<<<<<<< HEAD
=======
def test_messages_share_invalid_message(user_1, invalid_message_text, channel_public):
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_1['token'],
        "og_message_id": 1,
        "message": invalid_message_text,
        "channel_id": channel_public['channel_id'],
        "dm_id": -1
    })
    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96
def test_messages_share_toolong(user_1, user_2, channel_public, create_dm_2_user, invalid_message_text):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "hello world"
    })
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_1["token"],
        "og_message_id": 1,
        "message": invalid_message_text,
        "channel_id": channel_public['channel_id'],
        "dm_id": -1
    })
    assert request.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_messages_share_not_ch_member(user_1, user_2, channel_public, create_dm_2_user):
    r = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": 1,
        "message": "Hello World"
    })
    assert r.status_code == 200
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_2["token"],
        "og_message_id": 1,
        "message": "new message",
        "channel_id": channel_public['channel_id'],
        "dm_id": -1
    })
    assert request.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_messages_share_not_dm_member(user_1, user_3, create_dm_2_user, channel_public):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "hello"
    })
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_3['token'],
        "channel_id": channel_public["channel_id"],
    })
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_3["token"],
        "og_message_id": 1,
        "message": "new message",
        "channel_id": -1,
        "dm_id": create_dm_2_user["dm_id"],
    })
    assert request.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_messages_share_to_channel(user_1, user_2, create_dm_2_user, channel_public):
    r = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_2['token'],
        "dm_id": 1,
        "message": "Hello World",
    })
    assert r.status_code == 200
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_1["token"],
        "og_message_id": 1,
        "message": "new message",
        "channel_id": channel_public['channel_id'],
        "dm_id": -1
    })
    assert request.status_code == 200
    r = requests.get(f"{BASE_URL}/channel/messages/v2", params={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": 0
    })
    assert r.status_code == 200
    payload = r.json()
    payload["messages"][-1]["message"] = "sharing this to a channel Hello World"
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_messages_share_to_dm(user_1, user_2, create_dm_2_user, channel_public):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "Hello world"
    })
    request = requests.post(f"{BASE_URL}/message/share/v1", json={
        "token": user_1['token'],
        "og_message_id": 1,
        "message": "sharing this to a dm",
        "channel_id": -1,
        "dm_id": 1,
    })
    assert request.status_code == 200
    r = requests.get(f"{BASE_URL}/dm/messages/v1", params={
        "token": user_1["token"],
        "dm_id": 1,
        "start": 0
    })
    assert r.status_code == 200
    payload = r.json()
    payload["messages"][-1]["message"] = "sharing this to a dm Hello World"
    requests.delete(f"{BASE_URL}/clear/v1", json={})

# React tests


# def test_messages_react_successful(user_1, channel_public, message_text):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

<<<<<<< HEAD
#     assert send.status_code == 200
#     assert requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })
=======
    assert send.status_code == 200
    assert requests.post(f"{url}/message/react/v1", json={
        'token': user_1['token'],
        'message_id': payload['message_id'],
        'react_id': 1
    })
>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96

#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_react_successful_dm(user_1, c, message_text):
#     send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
#         "token": user_1['token'],
#         "dm_id": c['dm_id'],
#         "message": message_text
#     })
#     payload = send.json()

<<<<<<< HEAD
#     assert send.status_code == 200
#     assert requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })
=======
    assert send.status_code == 200
    assert requests.post(f"{url}/message/react/v1", json={
        'token': user_1['token'],
        'message_id': payload['message_id'],
        'react_id': 1
    })
>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96

#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_react_invalid_token(user_1, channel_public, message_text, user_invalid):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

<<<<<<< HEAD
#     requests.post(f"{url}/message/react", json={
#         'token': user_invalid,
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })
=======
    request = requests.post(f"{url}/message/react/v1", json={
        'token': user_invalid,
        'message_id': payload['message_id'],
        'react_id': 1
    })
>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


<<<<<<< HEAD
# def test_messages_react_invalid_message_id(user_1, channel_public, message_text, invalid_message_id):
#     requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     request = requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': invalid_message_id,
#         'react_id': 1
#     })
=======
def test_messages_react_invalid_message_id(user_1, channel_public, message_text, invalid_message_id):
    requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    request = requests.post(f"{url}/message/react/v1", json={
        'token': user_1['token'],
        'message_id': invalid_message_id,
        'react_id': 1
    })
>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


<<<<<<< HEAD
# def test_messages_react_invalid_dm_id(user_1, c, message_text, invalid_message_id):
#     requests.post(f"{BASE_URL}/message/senddm/v1", json={
#         "token": user_1['token'],
#         "dm_id": c['dm_id'],
#         "message": message_text
#     })
#     request = requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': invalid_message_id,
#         'react_id': 1
#     })
=======
def test_messages_react_invalid_dm_id(user_1, c, message_text, invalid_message_id):
    requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": c['dm_id'],
        "message": message_text
    })
    request = requests.post(f"{url}/message/react/v1", json={
        'token': user_1['token'],
        'message_id': invalid_message_id,
        'react_id': 1
    })
>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_react_invalid_react_id(user_1, channel_public, message_text, invalid_react_id):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

<<<<<<< HEAD
#     request = requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': invalid_react_id
#     })
=======
    request = requests.post(f"{url}/message/react/v1", json={
        'token': user_1['token'],
        'message_id': payload['message_id'],
        'react_id': invalid_react_id
    })
>>>>>>> 20a154533b01af2f9458aa1319c84765da499c96

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_react_already_reacted(user_1, channel_public, message_text):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })
#     request = requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})

# # Unreact tests


# def test_messages_unreact_successful(user_1, channel_public, message_text):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     request = requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })
#     assert request.status_code == 200
#     assert requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_unreact_successful_dm(user_1, c, message_text):
#     send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
#         "token": user_1['token'],
#         "dm_id": c['dm_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     request = requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })
#     assert request.status_code == 200
#     assert requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_unreact_invalid_token(user_1, channel_public, message_text, user_invalid):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     request = requests.post(f"{url}/message/unreact", json={
#         'token': user_invalid,
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_unreact_invalid_message_id(user_1, channel_public, message_text, invalid_message_id):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     request = requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': invalid_message_id,
#         'react_id': 1
#     })

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_unreact_invalid_dm_id(user_1, c, message_text, invalid_message_id):
#     send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
#         "token": user_1['token'],
#         "dm_id": c['dm_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     request = requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': invalid_message_id,
#         'react_id': 1
#     })

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_unreact_invalid_react_id(user_1, channel_public, message_text, invalid_react_id):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     request = requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': invalid_react_id
#     })

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


# def test_messages_react_already_unreacted(user_1, channel_public, message_text):
#     send = requests.post(f"{BASE_URL}/message/send/v1", json={
#         "token": user_1['token'],
#         "channel_id": channel_public['channel_id'],
#         "message": message_text
#     })
#     payload = send.json()

#     requests.post(f"{url}/message/react", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     request = requests.post(f"{url}/message/unreact", json={
#         'token': user_1['token'],
#         'message_id': payload['message_id'],
#         'react_id': 1
#     })

#     assert request.status_code == InputError.code
#     requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_pin_already_pinned(user_1, channel_public, message_text):
    request_send = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": "hello world"
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin_1 = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"],
    })
    assert request_pin_1.status_code == 200

    request_pin_2 = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"]
    })
    assert request_pin_2.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_unpin_not_pinned(user_1, channel_public, message_text):
    request_send = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_unpin = requests.post(f"{BASE_URL}/message/unpin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"]
    })
    assert request_unpin.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_nonowner_pin(user_1, user_2, channel_public, message_text):
    request_channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    assert request_channel_invite.status_code == 200

    request_send = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_2['token'],
        "message_id": payload["message_id"]
    })
    assert request_pin.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_nonowner_unpin(user_1, user_2, channel_public, message_text):
    request_channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    assert request_channel_invite.status_code == 200

    request_send = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"]
    })
    assert request_pin.status_code == 200

    request_unpin = requests.post(f"{BASE_URL}/message/unpin/v1", json={
        "token": user_2['token'],
        "message_id": payload["message_id"]
    })
    assert request_unpin.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_pin_already_pinned(user_1, create_dm_2_user, message_text):
    request_send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": create_dm_2_user['dm_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin_1 = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"],
    })
    assert request_pin_1.status_code == 200
    request_pin_2 = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"]
    })
    assert request_pin_2.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_unpin_not_pinned(user_1, user_2, create_dm_2_user, message_text):
    request_send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": create_dm_2_user['dm_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_unpin = requests.post(f"{BASE_URL}/message/unpin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"]
    })
    assert request_unpin.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_nonowner_pin(user_1, user_2, create_dm_2_user, message_text):
    request_send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": create_dm_2_user['dm_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_2['token'],
        "message_id": payload["message_id"]
    })
    assert request_pin.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_dm_nonowner_unpin(user_1, user_2, create_dm_2_user, message_text):
    request_send = requests.post(f"{BASE_URL}/message/senddm/v1", json={
        "token": user_1['token'],
        "dm_id": create_dm_2_user['dm_id'],
        "message": message_text
    })
    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": payload["message_id"]
    })
    assert request_pin.status_code == 200

    request_unpin = requests.post(f"{BASE_URL}/message/unpin/v1", json={
        "token": user_2['token'],
        "message_id": payload["message_id"]
    })
    assert request_unpin.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_pin_invalid_message(user_1, invalid_message_id):

    request_pin = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_1['token'],
        "message_id": invalid_message_id
    })
    assert request_pin.status_code == InputError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_message_pin_invalid_token(user_1, user_invalid, channel_public, message_text):

    request_send = requests.post(f"{BASE_URL}/message/send/v1", json={
        "token": user_1["token"],
        "channel_id": channel_public["channel_id"],
        "message": message_text
    })

    assert request_send.status_code == 200
    payload = request_send.json()

    request_pin = requests.post(f"{BASE_URL}/message/pin/v1", json={
        "token": user_invalid,
        "message_id": payload["message_id"],
    })

    assert request_pin.status_code == AccessError.code

    requests.delete(f"{BASE_URL}/clear/v1", json={})
