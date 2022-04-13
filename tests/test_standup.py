import tests.fixtures as fix
import time
from src.error import AccessError, InputError
NORMAL_LENGTH = 60  # seconds
INVALID_LENGTH = -1


def test_standup_start_invalid_token_payload(clear, user_invalid, channel_public):
    response = fix.standup_start_v1(
        user_invalid['token'], channel_public['channel_id'], NORMAL_LENGTH)
    assert response.status_code == AccessError.code


def test_standup_start_invalidated_token(clear, user_1, channel_public):
    fix.logout_v1(user_1['token'])
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    assert response.status_code == AccessError.code


def test_standup_start_invalid_token(clear, invalid_token, channel_public):
    response = fix.standup_start_v1(
        invalid_token, channel_public['channel_id'], NORMAL_LENGTH)
    assert response.status_code == AccessError.code


def test_standup_start_channel_access_error(clear, user_2, channel_public):
    response = fix.standup_start_v1(
        user_2['token'], channel_public['channel_id'], NORMAL_LENGTH)
    assert response.status_code == AccessError.code


def test_standup_start_invalid_channel_id(user_1, invalid_channel_id):
    response = fix.standup_start_v1(
        user_1['token'], invalid_channel_id, NORMAL_LENGTH)
    assert response.status_code == InputError.code


def test_standup_start_invalid_length(clear, user_1, channel_public):
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], INVALID_LENGTH)
    assert response.status_code == InputError.code


def test_standup_start_standup_active(clear, user_1, channel_public):
    fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    assert response.status_code == InputError.code


def test_standup_start(clear, user_1, channel_public):
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    response1 = fix.standup_active_v1(
        user_1['token'], channel_public['channel_id'])
    body = response.json()
    body1 = response1.json()
    assert body["time_finish"] == body1['time_finish']
    assert body1["is_active"] == True

# Standup Active


def test_standup_active_invalid_token_payload(clear, user_invalid, channel_public):
    response = fix.standup_active_v1(
        user_invalid['token'], channel_public['channel_id'])
    assert response.status_code == AccessError.code


def test_standup_active_invalidated_token(clear, user_1, channel_public):
    fix.logout_v1(user_1['token'])
    response = fix.standup_active_v1(
        user_1['token'], channel_public['channel_id'])
    assert response.status_code == AccessError.code


def test_standup_active_invalid_token(clear, invalid_token, channel_public):
    response = fix.standup_active_v1(
        invalid_token, channel_public['channel_id'])
    assert response.status_code == AccessError.code


def test_standup_active_channel_access_error(clear, user_2, channel_public):
    response = fix.standup_active_v1(
        user_2['token'], channel_public['channel_id'])
    assert response.status_code == AccessError.code


def test_standup_active_invalid_channel_id(clear, user_1, invalid_channel_id):
    response = fix.standup_active_v1(
        user_1['token'], invalid_channel_id)
    assert response.status_code == InputError.code


def test_standup_active(clear, user_1, channel_public):
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    response1 = fix.standup_active_v1(
        user_1['token'], channel_public['channel_id'])
    body = response.json()
    body1 = response1.json()
    assert body["time_finish"] == body1['time_finish']
    assert body1["is_active"] == True

# Standup Send


def test_standup_send_invalid_token_payload(clear, user_invalid, channel_public, message_text):
    response = fix.standup_send_v1(
        user_invalid['token'], channel_public['channel_id'], message_text)
    assert response.status_code == AccessError.code


def test_standup_send_invalidated_token(clear, user_1, channel_public, message_text):
    fix.logout_v1(user_1['token'])
    response = fix.standup_send_v1(
        user_1['token'], channel_public['channel_id'], message_text)
    assert response.status_code == AccessError.code


def test_standup_send_invalid_token(clear, invalid_token, channel_public, message_text):
    response = fix.standup_send_v1(
        invalid_token, channel_public['channel_id'], message_text)
    assert response.status_code == AccessError.code


def test_standup_send_channel_access_error(clear, user_2, channel_public, message_text):
    response = fix.standup_send_v1(
        user_2['token'], channel_public['channel_id'], message_text)
    assert response.status_code == AccessError.code


def test_standup_send_invalid_channel_id(clear, user_1, invalid_channel_id, message_text):
    response = fix.standup_send_v1(
        user_1['token'], invalid_channel_id, message_text)
    assert response.status_code == InputError.code


def test_standup_send_invalid_text_standup(clear, user_1, channel_public, invalid_message_text):
    fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    response = fix.standup_send_v1(
        user_1['token'], channel_public['channel_id'], invalid_message_text)
    assert response.status_code == InputError.code


def test_standup_send_nonactive_standup(clear, user_1, channel_public, message_text):
    reponse = fix.standup_send_v1(
        user_1['token'], channel_public['channel_id'], message_text)
    assert reponse.status_code == InputError


def test_standup_send(clear, user_1, user_2, channel_public, message_text):
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)
    fix.standup_send_v1(user_1['token'], channel_public, message_text)

    time.sleep(response['time_finish'] - time.time())

    response2 = fix.test_channel_messages_v2(
        user_1['token'], channel_public['channel_id'], 0)

    body = response.json()
    body2 = response2.json()

    assert body2['messages'] == [{
        "message_id": 1,
        "u_id": 1,
        "message_text": "michaelchai: Hello world",
        "time_sent": body["time_finish"]
    }]


def test_standup_send_empty(clear, user_1, user_2, channel_public, message_text):
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)

    time.sleep(response['time_finish'] - time.time())

    reponse2 = fix.test_channel_messages_v2(
        user_1['token'], channel_public['channel_id'], 0)

    body = reponse2.json()

    assert body['messages'] == [{

    }]


def test_standup_send_multiple_users(clear, user_1, user_2, channel_public, message_text):
    response = fix.standup_start_v1(
        user_1['token'], channel_public['channel_id'], NORMAL_LENGTH)

    fix.standup_send_v1(user_1['token'], channel_public, message_text)
    fix.standup_send_v1(user_2['token'], channel_public, message_text)

    time.sleep(response['time_finish'] - time.time())

    reponse2 = fix.test_channel_messages_v2(
        user_1['token'], channel_public['channel_id'], 0)

    body = reponse2.json()

    assert body['mesages'] == [{
        "message_id": 1,
        "u_id": 1,
        "message_text": "mikeytest: Hello world\n migueltest: Hello world",
        "time_sent": body["time_finish"]
    }]


def test_standup_send_multiple_messages_multiple_users(clear, user_1, user_2, channel_public, message_text):
    response = fix.standup_start_v1(
        user_2['token'], channel_public['channel_id'], NORMAL_LENGTH)

    for _ in range(0, 1):
        fix.standup_send_v1(user_1['token'], channel_public, message_text)
        fix.standup_send_v1(user_2['token'], channel_public, message_text)

    time.sleep(response['time_finish'] - time.time())

    response2 = fix.test_channel_messages_v2(
        user_1['token'], channel_public['channel_id'], 0)

    body = response2.json()

    assert body['messages'] == [{
        "message_id": 1,
        "u_id": 2,
        "message_text": """
        mikeytest: Hello world
        migueltest: Hello world
        mikeytest: Hello world
        migueltest: Hello world
        """,
        "time_sent": body["time_finish"]
    }]
