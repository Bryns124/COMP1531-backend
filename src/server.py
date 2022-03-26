from operator import methodcaller
import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config, data_store
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1
from src.message import messages_send_v1, message_senddm_v1
from src.channels import channels_list_v1, channels_listall_v1, channels_create_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.helper import save_data_store, load_data_store
from src.other import clear_v1
from src.user import users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1
from src.dm import dm_leave_v1, dm_messages_v1


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS

# Example
try:
    load_data_store()
except Exception:
    pass


@APP.route("/auth/login/v2", methods=['POST'])
def login_v2():
    data = request.get_json()
    body = auth_login_v1(data["email"], data["password"])
    return dumps({
        "token": body['token'],
        "auth_user_id": body['auth_user_id']
    })


@APP.route("/auth/register/v2", methods=['POST'])
def auth_register_v2():
    data = request.get_json()
    body = auth_register_v1(
        data['email'], data['password'], data['name_first'], data['name_last'])
    save_data_store()
    return dumps({
        'token': body['token'],
        'auth_user_id': body['auth_user_id']
    })


@APP.route("/auth/logout/v1", methods=['POST'])
def auth_logout():
    data = request.get_json()
    auth_logout_v1(data['token'])
    save_data_store()
    return dumps({

    })


@APP.route("/channels/create/v2", methods=['POST'])
def channels_create_v2():
    data = request.args.to_dict()
    body = channels_create_v1(
        data['token'], data['name'], data['is_public'])
    save_data_store()
    return dumps({
        'channel_id': body['channel_id']
    })


@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    data = request.args.to_dict()
    body = channels_list_v1(data['token'])
    return dumps({
        'channels': body['channels']
    })


@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    data = request.get_json()
    body = channels_listall_v1(data['token'])
    return dumps({
        'channels': body['channels']
    })

@APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    data = request.get_json()
    channel_join_v1(data['token'], data['channel_id'])
    return dumps({

    })


@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    data = request.args.to_dict()
    body = channel_details_v1(data['token'], data['channel_id'])
    return dumps({
        "name": body['name'],
        "is_public": body['is_public'],
        "owner_members": body['owner_members'],
        "all_members": body['all_members']
    })


@APP.route("/channel/invite/v2", methods=['POST'])
def channel_invite_v2():
    data = request.get_json()
    channel_invite_v1(
        data['token'], data['channel_id'], data['u_id'])
    return dumps({

    })


@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2():
    data = request.args.to_dict()
    body = channel_messages_v1(
        data['token'], data['channel_id'], data['start'])
    return dumps({
        'messages': body['messages'],
        'start': body['start'],
        'end': body['end']
    })

# Havent written the test functions and function


@APP.route("/channel/leave/v1", methods=['POST'])
def channel_leave():
    data = request.get_json()
    channel_leave_v1(
        data['token'], data['channel_id'])
    return dumps({

    })


# Need to write functions for channel addowner and removeowner
# and successful tests like addowner and removeowner successfully
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    channel_addowner_v1(
        data['token'], data['channel_id'], data['u_id'])
    return dumps({

    })


@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    channel_removeowner_v1(
        data['token'], data['channel_id'], data['u_id'])
    return dumps({

    })


@APP.route("/clear/v1", methods=['DELETE'])
def clear_v2():
    clear_v1()
    return dumps({

    })


@APP.route("/channel/messages/v2", methods=['GET'])
def channel_message_v2():
    data = request.args.to_dict()
    body = channel_messages_v1(
        data['token'], data['channel_id'], data['start'])
    return dumps({
        "messages": body['messages'],
        "start": body['start'],
        "end": body['end']

    })


@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    body = request.get_json()
    data = messages_send_v1(body['token'], body['channel_id'], body['message'])
    return dumps({
        "message_id": data['message_id']
    })



@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })


@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    data = request.args.get()
    body = users_all_v1(data['token'])
    return dumps({
        'users': body['users']
    })


@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    data = request.args.get()
    body = user_profile_v1(data['token'], data['u_id'])
    return dumps({
        'user': body['user']
    })


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()
    user_profile_setname_v1(
        data['token'], data['name_first'], data['name_last'])
    return dumps({})


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
    data = request.get_json()
    user_profile_setemail_v1(data['token'], data['email'])
    return dumps({})


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    user_profile_sethandle_v1(data['token'], data['handle_str'])
    return dumps({})


@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    body = dm_create_v1(data['token'], data['u_ids'])

    return dumps({
        "dm_id": body["dm_id"]
    })


@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    data = request.args.to_dict()
    body = dm_list_v1(data["token"])

    return dumps({
        'dms': body['dms']
    })


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    dm_remove_v1(data['token'], data["dm_id"])
    return dumps({})


@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    data = request.args.to_dict()
    body = dm_details_v1(data["token"], int(data["dm_id"]))
    return dumps({
        "name": body["name"],
        "members": body["members"]
    })


@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    dm_leave_v1(data['token'], data["dm_id"])
    return dumps({})


@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    data = request.args.to_dict()
    body = dm_messages_v1(data["token"], int(data["dm_id"]), int(data["start"]))

    return dumps({
        "messages": body["messages"],
        "start": body["start"],
        "end": body["end"]
    })


@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    data = request.get_json()
    body = message_senddm_v1(data["token"], data["dm_id"], data["message"])

    return dumps({
        "message_id": body["message_id"]
    })


# @ APP.route("/channels/listall/v2", method = ['POST'])
# def channels_listall_v2():
#     data=request.get_json()
#     body=channels_listall_v1(data['token'])
#     return dumps({
#         'channels': body['channels']
#     })
# wew14
# NO NEED TO MODIFY BELOW THIS POINT

if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port, debug=True)  # Do not edit this port
