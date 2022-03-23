from src.auth import auth_register_v1
from src.dm import dm_create_v1, dm_details_v1, dm_remove_v1
from src.other import clear_v1
from src.error import InputError, AccessError
from src.helper import SECRET
import jwt
import pytest

'''Users'''
@pytest.fixture()
def user_1():
    return auth_register_v1("mikey@unsw.com", "test123456", "Mikey", "Test")

@pytest.fixture
def user_2():
    return auth_register_v1("miguel@unsw.com", "test123456", "Miguel", "Test")

@pytest.fixture
def user_3():
    return auth_register_v1("matthew@unsw.com", "test123456", "Matthew", "Test")

'''DMs'''
@pytest.fixture
def dm_1(user_1, user_2):
    return dm_create_v1(user_1["token"], [2])

@pytest.fixture
def dm_2(user_1, user_2, user_3):
    return dm_create_v1(user_3["token"], [1, 2])

@pytest.fixture
def dm_3(user_1, user_2, user_3):
    return dm_create_v1(user_3["token"], [2, 1])

@pytest.fixture
def invalid_dm_id():
    return -1
'''
tests for dm_details
test for input error when dm_id is invalid
test for access error when dm_id is valid and the authorised user is not a member of the dm
create users, create dm, check that the dm details are correct

'''
# Input Error

def test_input_error_dm_details_v1(user_1, invalid_dm_id):
    with pytest.raises(InputError):
        dm_details_v1(user_1["token"], invalid_dm_id)
    clear_v1()

def test_access_error_dm_details_v1(user_1, user_2, user_3, dm_1):
    with pytest.raises(AccessError):
        dm_details_v1(user_3["token"], dm_1["dm_id"])
    clear_v1()

def test_dm_1_dm_details_v1(user_1, user_2, dm_1):
    assert dm_details_v1(user["token"], 1) == {
        "name": "migueltest, mikeytest", 
        "members": [
            {
                "u_id": 1, 
                "email": "mikey@unsw.com",
                "name_first": "Mikey",
                "name_last": "Test",
                "handle_str": "mikeytest"
            },
            {
                "u_id": 2,
                "email": "miguel@unsw.com",
                "name_first": "Miguel",
                "name_last": "Test",
                "handle_str": "migueltest"
            }
        ]
    }
    clear_v1()

def test_dm_2_dm_details(user_1, user_2, user_3, dm_2)
    assert dm_details_v1(user["token"], 2) == {
        "name": "matthewtest, migueltest, mikeytest", 
        "members": [
            {
                "u_id": 3, 
                "email": "matthew@unsw.com",
                "name_first": "Matthew",
                "name_last": "Test",
                "handle_str": "matthewtest"
            },
            {
                "u_id": 1, 
                "email": "mikey@unsw.com",
                "name_first": "Mikey",
                "name_last": "Test",
                "handle_str": "mikeytest"
            },
            {
                "u_id": 2,
                "email": "miguel@unsw.com",
                "name_first": "Miguel",
                "name_last": "Test",
                "handle_str": "migueltest"
            }
        ]
    }
    clear_v1()

def test_dm_3_dm_details(user_1, user_2, user_3, dm_2)
    assert dm_details_v1(user["token"], 2) == {
        "name": "matthewtest, migueltest, mikeytest", 
        "members": [
            {
                "u_id": 3, 
                "email": "matthew@unsw.com",
                "name_first": "Matthew",
                "name_last": "Test",
                "handle_str": "matthewtest"
            },
            {
                "u_id": 2,
                "email": "miguel@unsw.com",
                "name_first": "Miguel",
                "name_last": "Test",
                "handle_str": "migueltest"
            },
            {
                "u_id": 1, 
                "email": "mikey@unsw.com",
                "name_first": "Mikey",
                "name_last": "Test",
                "handle_str": "mikeytest"
            },
        ]
    }
    clear_v1()
'''
dm_remove
input error when the dm id is invalid
access error dm_id is valid and authorised user is not the original dm creator
access error dm_id is valid and the authorised user is not part of the dm anymore

create users and dm to users, then run dm_remove, check that dm has no members
'''