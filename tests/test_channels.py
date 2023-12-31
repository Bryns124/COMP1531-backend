import pytest
from src.channels import channels_listall_v1, channels_create_v1, channels_list_v1
from src.auth import auth_register_v1
from src.channel import channel_join_v1
from src.other import clear_v1
from src.error import AccessError, InputError

from src.config import port, url

BASE_URL = url
@pytest.fixture
def user_1():
    return auth_register_v1('alice@gmail.com', '123456', 'Alice', 'Wan')


@pytest.fixture
def user_2():
    return auth_register_v1('adi@gmail.com', 'abcdef', 'Adiyat', 'Rahman')


@pytest.fixture  # user1 creates a public channel
def public_channel_user1(user_1):
    return channels_create_v1(user_1['token'], 'Public', True)


@pytest.fixture  # user2 creates a private channel
def private_channel_user2(user_2):
    return channels_create_v1(user_2['token'], 'Private', False)


@pytest.fixture  # user1 creates a public channel
def private_second_channel_user1(user_1):
    return channels_create_v1(user_1['token'], 'User_1_Private', False)


def test_listall_no_channel(user_1):
    '''
    test for if no channels have been created
    '''
    assert channels_listall_v1(user_1['token']) == {
        'channels': []
    }
    clear_v1()


def test_listall_public(user_1, public_channel_user1):
    '''
    test for listing public channels
    '''
    assert channels_listall_v1(user_1['token']) == {
        'channels': [
            {
                'channel_id': public_channel_user1['channel_id'],
                'name': 'Public'
            }
        ]
    }
    clear_v1()


def test_listall_private(user_2, private_channel_user2):
    '''
    test for listing private channel
    '''
    assert channels_listall_v1(user_2['token']) == {
        'channels': [
            {
                'channel_id': private_channel_user2['channel_id'],
                'name': 'Private'
            }
        ]
    }
    clear_v1()


def test_listall_both(user_1, user_2, public_channel_user1, private_channel_user2):
    '''
    test if two channels are created by separate users
    '''
    assert channels_listall_v1(user_1['token']) == {
        'channels': [
            {
                'channel_id': public_channel_user1['channel_id'],
                'name': 'Public'
            },
            {
                'channel_id': private_channel_user2['channel_id'],
                'name': 'Private'
            }
        ]
    }
    clear_v1()


def test_create_public_channel(user_2):
    '''
    Test to check if creating a new public channel return the channel-id of that channel
    Assumption: The token is correct
    '''
    assert channels_create_v1(user_2['token'], 'public_channel', True) == {
        'channel_id': 1
    }
    clear_v1()


def test_create_private_channel(user_2):
    '''
    Test to check if creating a new private channel will return the correct channel_id
    Assumption: The token is correct
    '''
    assert channels_create_v1(user_2['token'], 'test_channel', False) == {
        'channel_id': 1
    }
    clear_v1()


def test_create_channel_invalid_name_1(user_2):
    '''
    Test to check if creating a channel with an invalid name of less than 1 character raises an Input Error
    Assumption: The token is correct
    '''
    with pytest.raises(InputError):
        assert channels_create_v1(user_2['token'], '', True)
    clear_v1()


def test_create_channel_invalid_name_2(user_2):
    '''
    Test to check if creating a new channel with an invalid name of more than 20 characters raises an Input Error
    Assumption: The token is correct
    '''
    with pytest.raises(InputError):
        assert channels_create_v1(
            user_2['token'], 'abcdefghijklmnopqrstuv', True)
    clear_v1()


def test_create_multiple_channel(user_2):
    '''
    Test to check if creating multiple channels will return sequential channel_ids
    Assumption: the channels will not be sorted by their name in alphabetical order
    '''
    assert channels_create_v1(user_2['token'], 'channel_1', True) == {
        'channel_id': 1
    }
    assert channels_create_v1(user_2['token'], 'channel_2', True) == {
        'channel_id': 2
    }
    clear_v1()


def test_channel_list_private(user_2, private_channel_user2):
    '''
    Test to check if a member of a private channel can list all the channels he is a member of
    Assumption: The token is correct
    Assumption: The user is only a member of one channel
    '''
    assert channels_list_v1(user_2['token']) == {
        'channels': [
            {
                'channel_id': private_channel_user2['channel_id'],
                'name': 'Private',
            }
        ]
    }
    clear_v1()


def test_channel_list_public(user_1, public_channel_user1):
    '''
    Test to check if a member of a public channel can list all the channels he is a member of
    Assumption: The token is correct
    Assumption: The user is only a member of one channel
    '''
    assert channels_list_v1(user_1['token']) == {
        'channels': [
            {
                'channel_id': public_channel_user1['channel_id'],
                'name': 'Public',
            }
        ]
    }
    clear_v1()


def test_channel_list_empty(user_2):
    '''
    Test to check if an empty list of dictionaries is returned if the user is not a member of any channels
    Assumption: The token is correct
    '''
    assert channels_list_v1(user_2['token']) == {
        'channels': []
    }
    clear_v1()


def test_channel_list_multiple_created(user_1, public_channel_user1, private_second_channel_user1):
    '''
    Test to check if a list of dictionaries containing channel details is correctly generated,
    when the user creates and is the owner of multiple channels
    Assumption: The token is correct
    '''
    assert channels_list_v1(user_1['token']) == {
        'channels': [
            {
                'channel_id': public_channel_user1['channel_id'],
                'name': 'Public',
            },
            {
                'channel_id': private_second_channel_user1['channel_id'],
                'name': 'User_1_Private',
            }
        ]
    }
    clear_v1()
