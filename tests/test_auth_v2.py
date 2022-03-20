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


@pytest.fixture
def message_text():
    return "Hello world"


@pytest.fixture
def invalid_message_text_short():
    return ""


def invalid_message_text():
    return "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. N"


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

def test_auth_register_user_created_sucessfully_v2():
    request_register = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })
    request_login = requests.post(f"{BASE_URL}/auth/login/v2", json={
        "email": email,
        "password": password
    })
    # assert response.status_code == 200
    assert request_register.json() == request_login.json()

def test_register_invalid_email_v2():
    # not sure how to fit all the invalid email cases
    request_register = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })
    assert request_register.status_code == InputError.code


def test_register_email_already_used_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })
    request_register2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })
    assert request_register1.status_code == 200
    assert request_register2.status_code == InputError.code

def test_register_returns_unique_ID_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })
    request_register2 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": email,
        "password": password,
        "name_first": name_first,
        "name_last": name_last
    })
    assert request_register1.json() != request_register2.json()

def test_password_length_less_than_6_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "pass",
        "name_first": "Bryan",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code


def test_first_name_length_less_than_1_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code

def test_first_name_length_more_than_50_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn",
        "name_last": "Le"
    })
    assert request_register1.status_code == InputError.code

def test_last_name_length_less_than_1_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": ""
    })
    assert request_register1.status_code == InputError.code

def test_last_name_length_more_than_50_v2():
    request_register1 = requests.post(f"{BASE_URL}/auth/register/v2", json={
        "email": "bryanle@gmail.com",
        "password": "password123",
        "name_first": "Bryan",
        "name_last": "qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbn"
    })
    assert request_register1.status_code == InputError.code

def test_handle_generated_correctly_v2():
    pass

