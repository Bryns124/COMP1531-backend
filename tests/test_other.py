import pytest

from src.other import clear_v1
from src.auth import auth_register_v1
from src.channels import channels_create_v1


@pytest.fixture
def user_1():
    return auth_register_v1('alice@gmail.com', '123456', 'Alice', 'Wan')


@pytest.fixture
def user_2():
    return auth_register_v1('john@gmail.com', 'abcdef', 'John', 'Smith')


def test_clear_empty():
    assert clear_v1() == {}
    clear_v1()


def test_clear_user(user_1, user_2):
    assert clear_v1() == {}
    clear_v1()


def test_clear_channel(user_1, user_2):
    channels_create_v1(user_1['token'], 'Public', True)
    channels_create_v1(user_2['token'], 'Private', False)
    assert clear_v1() == {}
    clear_v1()
