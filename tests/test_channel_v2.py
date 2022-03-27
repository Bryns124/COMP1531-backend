from distutils.command.config import config
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1
from src.channels import channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
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
def invalid_user_id():
    return jwt.encode({'auth_user_id': -1, 'session_id': 1}, SECRET, algorithm="HS256")


"""Channels"""


@pytest.fixture
def channel_public(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "Test Channel",
        "is_public": True
    })
    return r.json()


@pytest.fixture
def channel_private_access(user_no_access):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_no_access['token'],
        "name": "No Access Channel",
        "is_public": False
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
def channel_1(user_1):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_1['token'],
        "name": "A New Hope",
        "is_public": True
    })
    return r.json()


@pytest.fixture
def channel_2(user_2):
    r = requests.post(f"{BASE_URL}/channels/create/v2", json={
        "token": user_2['token'],
        "name": "Empire Strikes Back",
        "is_public": True
    })
    return r.json()


@pytest.fixture
def invalid_channel():
    return {
        'channel_id': -1
    }


@pytest.fixture
def starting_value():
    return 0


def test_channel_invite_access_error(user_1, channel_private_access, user_2):
    """
    This test checks to see that a AccessError is raised when attmepting to invite someone to a channel,
    but they do not have the access privlieges to do so.
    Args:
        user_1 (u_id): User who is not apart of the private channel
        channel_private (channel_id): The private channel_id
        user_no_access (u_id): User who is going to  be invited
    """
    request_channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_private_access['channel_id'],
        "u_id": user_2["auth_user_id"]
    })
    assert request_channel_invite.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_invite_channel_id_error(user_1, invalid_channel_id, user_2):
    """
    This test checks to see that a InputError is raised when attemtping to invite someone to
    a channel with a invalid channel_id
    Args:
        user_1 (_type_): The u_id of the person executing the command and inviting.
        invalid_channel_id (_type_): The invalid channel_id
        user_2 (_type_): The u_id of the person being invited
    """
    request_channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": invalid_channel_id,
        "u_id": user_2["auth_user_id"]
    })
    assert request_channel_invite.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_invite_u_id_error(user_1, channel_public, user_invalid):
    """
    This test checks to see that a InputError is raised when attemtping to invite someone with
    an invalid u_id.
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting.
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.
        user_invalid (u_id): The invalid u_id
    """
    request_channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_invalid
    })
    assert request_channel_invite.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_invite_u_id_member(user_1, channel_public, user_2):
    """
    This test checks to see that a InputError is raised when attempting invite someone
    to a channel who is already apart of that channel.
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting.
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.
        user_2 (u_id): The u_id of the person that is already in the channel.
    """
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    request_channel_invite = requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    assert request_channel_invite.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_invite(user_1, channel_public, user_2):
    """
    This test verifies that when a user is invited to a channel they successfully become a member
    Args:
        user_1 (u_id): The u_id of the person executing the command and inviting.
        channel_public (channel_id): Takes the channel_id that user_1 is inviting to.
        user_2 (u_id): The u_id of the person being invited.
    """
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    r = requests.get(f"{BASE_URL}/channels/list/v2", json={
        "token": user_2["token"]
    })
    assert r.json()[
        'channels'][-1]['channel_id'] == channel_public['channel_id']
    requests.delete(f"{BASE_URL}/clear/v1", json={})

    # channel_invite_v1(user_1['token'], channel_public['channel_id'], user_2['auth_user_id'])
    # assert channels_list_v1(user_2['token'])['channels'][-1]['channel_id'] == channel_public['channel_id']
    # clear_v1()


def test_channel_messages_v1_channel_id_error(user_1, invalid_channel_id):
    """
    This function tests that a id_error is raised when the user is trying to access the messages for
    a invalid channel_id
    Args:
        user_1 (u_id): Id of the user who is attempting to read a channel's messages
        invalid_channel_id (channel_id): The invalid channel id
        start (start): Where the user wants to start indexing the messages from
    """
    request_channel_messages = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "start": 0
    })
    assert request_channel_messages.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_messages_v1_access_error(user_no_access, channel_public):
    """
    This function tests that a exception is raised when a user tries to read the messages
    of a channel they do not have access to.
    Args:
        user_no_access (u_id): Id of the user who has no access to read the channel messages
        channel_public (channel_id): Id of the channel the user is trying to access
        start start): Starting index
    """
    request_channel_messages = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_no_access['token'],
        "channel_id": channel_public['channel_id'],
        "start": 0
    })
    assert request_channel_messages.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_messages_v1(user_1, channel_public):
    """
    This test checks to see that no messages are present when after creating a channel
    Args:
        user_1 (u_id): The id of the user trying to read the messages in a channel
        channel_public (channel_id): The channel_id the user is trying to access
        first_message (start_): Starting index of the messages
    """
    request_channel_messages = requests.get(f"{BASE_URL}/channel/messages/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "start": 0
    })
    assert request_channel_messages.json() == {
        'messages': [],
        'start': 0,
        'end': -1}
    requests.delete(f"{BASE_URL}/clear/v1", json={})


# Tests for channel/addowner
def test_channel_addowner(user_1, user_2, channel_public):
    """
    This test makes a user an owner of the channel.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
    })
    requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    request_channel_details = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })
    data = request_channel_details.json()
    assert data == {
        'name': 'Test Channel',
        'is_public': True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
             'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
             'name_last': 'Test', 'handle_str': 'migueltest'}
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
             'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
             'name_last': 'Test', 'handle_str': 'migueltest'}
        ]
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_addowner_invalid_channel(channel_public, invalid_channel_id, user_1):
    """
    This test checks to see that a InputError is raised when channel is invalid.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
    })
    request_channel_add_owner = requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "u_id": user_1['auth_user_id']
    })
    assert request_channel_add_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_addowner_invalid_user(channel_public, invalid_user_id, user_1):
    """
    This test checks to see that a InputError is raised when user is invalid.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
    })
    request_channel_add_owner = requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": invalid_user_id
    })
    assert request_channel_add_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_addowner_owner_not_in_channel(user_1, user_2, channel_public):
    """
    This test checks to see that a InputError is raised when owner is not a member 
    of that channel.
    """
    request_channel_add_owner = requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    assert request_channel_add_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_addowner_user_already_owner(user_1, user_2, channel_public):
    """
    This test checks to see that a InputError is raised when user is already an
    owner of the channel.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })

    request_channel_add_owner = requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    assert request_channel_add_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_addowner_user_not_owner(user_2, user_no_access, channel_public):
    """
    This test checks to see that an AccessError is raised when channel is
    valid and the authorised user does not have owner permissions in the channel
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })

    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_no_access['token'],
        "channel_id": channel_public['channel_id']
    })

    request_channel_add_owner = requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_no_access['auth_user_id']
    })
    assert request_channel_add_owner.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


# Tests for channel/removeowner
def test_channel_removeowner(user_1, user_2, channel_public):
    """
    This test removes an user as an owner of the channel.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
    })
    requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    requests.post(f"{BASE_URL}/channel/removeowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    request_channel_details = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })
    data = request_channel_details.json()
    assert data == {
        'name': 'Test Channel',
        'is_public': True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
             'name_last': 'Test', 'handle_str': 'mikeytest'},
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
             'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
             'name_last': 'Test', 'handle_str': 'migueltest'}
        ]
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_removeowner_invalid_channel(channel_public, invalid_channel_id, user_1):
    """
    This test checks to see that a InputError is raised when channel is invalid.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
    })
    requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_1['auth_user_id']
    })
    request_channel_remove_owner = requests.post(f"{BASE_URL}/channel/removeowner/v1", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id,
        "u_id": user_1['auth_user_id']
    })
    assert request_channel_remove_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_removeowner_invalid_user(channel_public, invalid_user_id, user_1, user_2):
    """
    This test checks to see that a InputError is raised when user is invalid.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
    })
    requests.post(f"{BASE_URL}/channel/addowner/v1", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_1['auth_user_id']
    })
    request_channel_remove_owner = requests.post(f"{BASE_URL}/channel/removeowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": invalid_user_id
    })
    assert request_channel_remove_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_removeowner_user_not_owner(user_1, user_2, channel_public):
    """
    This test checks to see that an InputError is raised when removing the u_id
    of a user who is not an owner of the channel.
    """
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
    })

    request_channel_remove_owner = requests.post(f"{BASE_URL}/channel/removeowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    assert request_channel_remove_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_removeowner_only_one_owner(user_1, user_2, channel_public):
    """
    This test checks to see that an InputError is raised when removing the only
    owner of the channel.
    """
    request_channel_remove_owner = requests.post(f"{BASE_URL}/channel/removeowner/v1", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id'],
        "u_id": user_2['auth_user_id']
    })
    assert request_channel_remove_owner.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_details_input_error(user_1, invalid_channel_id):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_details_access_error(user_2, channel_public):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_details_wrong_u_id(user_invalid, channel_public):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_invalid,
        "channel_id": channel_public['channel_id']
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_details(user_1, channel_public):
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id']
    })
    data = r.json()
    assert data == {
        'name': "Test Channel",
        'is_public': True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ]
    }
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_details_multiple_users(user_1, channel_public, user_2):
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id']
    })
    data = r.json()
    assert data == {
        'name': "Test Channel",
        'is_public': True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
                'name_last': 'Test', 'handle_str': 'migueltest'}
        ]
    }
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={

    })


def test_channel_join_channel_id_error(user_1, invalid_channel_id):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": invalid_channel_id
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_join_already_member_error(user_1, channel_public):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_1['token'],
        "channel_id": channel_public['channel_id']
    })
    assert r.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_join_access_error(user_2, channel_private):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_private['channel_id']
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_join_invalid_token(user_invalid, channel_public):
    r = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_invalid,
        "channel_id": channel_public['channel_id']
    })
    assert r.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_channel_join(channel_public, user_2):
    requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })
    r = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2['token'],
        "channel_id": channel_public['channel_id']
    })
    data = r.json()
    assert data == {
        'name': "Test Channel",
        'is_public':  True,
        'owner_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'}
        ],
        'all_members': [
            {'u_id': 1, 'email': 'mikey@unsw.com', 'name_first': 'Mikey',
                'name_last': 'Test', 'handle_str': 'mikeytest'},
            {'u_id': 2, 'email': 'miguel@unsw.com', 'name_first': 'Miguel',
                'name_last': 'Test', 'handle_str': 'migueltest'}
        ]
    }
    assert r.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_invalid_channel_id_channel_leave_v1(user_1, invalid_channel_id):
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": user_1["token"],
        "channel_id": invalid_channel_id
    })

    assert response.status_code == InputError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_auth_user_not_in_channel_channel_leave_v1(user_1, channel_2):
    response = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": user_1["token"],
        "channel_id": channel_2["channel_id"]
    })

    assert response.status_code == AccessError.code
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_only_user_leaves_channel_leave_v1(user_1, user_2, channel_1):
    response1 = requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": user_1["token"],
        "channel_id": channel_1["channel_id"]
    })
    assert response1.status_code == 200

    response2 = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1["token"],
        "channel_id": channel_1["channel_id"]
    })

    assert response2.status_code == AccessError.code

    response3 = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_1["channel_id"]
    })

    assert response3.status_code == 200
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_only_owner_leaves(user_1, user_2, channel_1):
    requests.post(f"{BASE_URL}/channel/invite/v2", json={
        "token": user_1["token"],
        "channel_id": channel_1["channel_id"],
        "u_id": user_2["auth_user_id"]
    })

    requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": user_1["token"],
        "channel_id": channel_1["channel_id"]
    })

    response = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_2["token"],
        "channel_id": channel_1["channel_id"]
    })

    payload = response.json()

    assert response.status_code == 200
    assert payload == {
        "name": "A New Hope",
        "is_public": True,
        "owner_members": [],
        "all_members": [
            {'email': 'miguel@unsw.com', 'handle_str': 'migueltest',
                'name_first': 'Miguel', 'name_last': 'Test', 'u_id': 2}
        ]
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})


def test_user_2_leaves_channel_leave_v1(user_1, user_2, channel_1):
    response1 = requests.post(f"{BASE_URL}/channel/join/v2", json={
        "token": user_2["token"],
        "channel_id": channel_1["channel_id"]
    })
    assert response1.status_code == 200

    requests.post(f"{BASE_URL}/channel/leave/v1", json={
        "token": user_2["token"],
        "channel_id": channel_1["channel_id"]
    })

    response2 = requests.get(f"{BASE_URL}/channel/details/v2", json={
        "token": user_1["token"],
        "channel_id": channel_1["channel_id"]
    })

    payload = response2.json()

    assert payload == {
        "name": "A New Hope",
        "is_public": True,
        "owner_members": [{'email': 'mikey@unsw.com', 'handle_str': 'mikeytest', 'name_first': 'Mikey', 'name_last': 'Test', 'u_id': 1}],
        "all_members": [{'email': 'mikey@unsw.com', 'handle_str': 'mikeytest', 'name_first': 'Mikey', 'name_last': 'Test', 'u_id': 1}]
    }
    requests.delete(f"{BASE_URL}/clear/v1", json={})
