import signal
from json import dumps
from flask import Flask, request, send_from_directory
from flask_mail import Mail, Message
from flask_cors import CORS
from src import config
from src.auth import auth_login_v1, auth_register_v1, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.message import messages_send_v1, message_senddm_v1, message_edit_v1, message_remove_v1, search_v1, message_share_v1, message_sendlater_v1, message_sendlaterdm_v1, message_react_v1, message_unreact_v1, message_pin_v1, message_unpin_v1
from src.channels import channels_list_v1, channels_listall_v1, channels_create_v1
from src.channel import channel_details_v1, channel_join_v1, channel_invite_v1, channel_messages_v1, channel_leave_v1, channel_addowner_v1, channel_removeowner_v1
from src.helper import save_data_store, load_data_store
from src.other import clear_v1
from src.user import user_profile_uploadphoto_v1, users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1, user_stats_v1, users_stats_v1
# from src.user import user_profile_uploadphoto_v1
from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.dm import dm_create_v1, dm_list_v1, dm_remove_v1, dm_details_v1, dm_leave_v1, dm_messages_v1
from src.standup import standup_active_v1, standup_send_v1, standup_start_v1
from src.notifications import notifications_get_v1

EMAIL_ADDRESS = "w17a.ant@gmail.com"
EMAIL_PASSWORD = """BirdsAren'tReal"""


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


APP = Flask(__name__, static_url_path='/static/')
CORS(APP)
mail = Mail(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

APP.config['MAIL_SERVER'] = 'smtp.gmail.com'
APP.config['MAIL_PORT'] = 465
APP.config['MAIL_USERNAME'] = EMAIL_ADDRESS
APP.config['MAIL_PASSWORD'] = EMAIL_PASSWORD
APP.config['MAIL_USE_TLS'] = False
APP.config['MAIL_USE_SSL'] = True
mail = Mail(APP)

# I modified above this point - sorry
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
    save_data_store()
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
    data = request.get_json()
    body = channels_create_v1(
        data['token'], data['name'], data['is_public'])
    save_data_store()
    return dumps({
        'channel_id': body['channel_id']
    })


@APP.route("/channels/list/v2", methods=['GET'])
def channels_list_v2():
    token = request.args.get('token')
    body = channels_list_v1(token)
    return dumps({
        'channels': body['channels']
    })


@APP.route("/channels/listall/v2", methods=['GET'])
def channels_listall_v2():
    token = request.args.get('token')
    body = channels_listall_v1(token)
    return dumps({
        'channels': body['channels']
    })


@ APP.route("/channel/join/v2", methods=['POST'])
def channel_join_v2():
    data = request.get_json()
    channel_join_v1(data['token'], data['channel_id'])
    save_data_store()
    return dumps({

    })


@APP.route("/channel/details/v2", methods=['GET'])
def channel_details_v2():
    # data = request.args.to_dict()
    # body = channel_details_v1(data['token'], int(data['channel_id']))

    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))

    body = channel_details_v1(token, channel_id)
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
    save_data_store()
    return dumps({

    })


@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages_v2():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    start = int(request.args.get('start'))

    body = channel_messages_v1(token, channel_id, start)
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
    save_data_store()
    return dumps({

    })


# Need to write functions for channel addowner and removeowner
# and successful tests like addowner and removeowner successfully
@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    channel_addowner_v1(
        data['token'], data['channel_id'], data['u_id'])
    save_data_store()
    return dumps({

    })


@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    channel_removeowner_v1(
        data['token'], data['channel_id'], data['u_id'])
    save_data_store()
    return dumps({

    })


@APP.route("/clear/v1", methods=['DELETE'])
def clear_v2():
    clear_v1()
    save_data_store()
    return dumps({

    })


# @APP.route("/channel/messages/v2", methods=['GET'])
# def channel_message_v2():
#     data = request.args.to_dict()
#     body = channel_messages_v1(
#         data['token'], data['channel_id'], data['start'])
#     return dumps({
#         "messages": body['messages'],
#         "start": body['start'],
#         "end": body['end']

#     })


@APP.route("/message/send/v1", methods=['POST'])
def message_send():
    body = request.get_json()
    data = messages_send_v1(body['token'], body['channel_id'], body['message'])
    save_data_store()
    return dumps({
        'message_id': data['message_id']
    })


# @APP.route("/echo", methods=['GET'])
# def echo():
#     data = request.args.get('data')
#     if data == 'echo':
#         raise InputError(description='Cannot echo "echo"')
#     return dumps({
#         'data': data
#     })


@APP.route("/users/all/v1", methods=['GET'])
def users_all():
    # data = request.get_json()
    token = request.args.get('token')

    body = users_all_v1(token)
    return dumps({
        'users': body['users']
    })


@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    token = request.args.get('token')
    u_id = int(request.args.get('u_id'))

    # data = request.get_json()
    body = user_profile_v1(token, u_id)
    return dumps({
        'user': body['user']
    })


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_profile_setname():
    data = request.get_json()
    user_profile_setname_v1(
        data['token'], data['name_first'], data['name_last'])
    save_data_store()
    return dumps({})


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_profile_setemail():
    data = request.get_json()
    user_profile_setemail_v1(data['token'], data['email'])
    save_data_store()
    return dumps({})


@APP.route("/message/edit/v1", methods=['PUT'])
def message_edit():
    data = request.get_json()
    message_edit_v1(data["token"], data["message_id"], data["message"])
    save_data_store()
    return dumps({})


@APP.route("/message/remove/v1", methods=['DELETE'])
def message_remove():
    data = request.get_json()
    message_remove_v1(data["token"], data["message_id"])
    save_data_store()
    return dumps({})


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_profile_sethandle():
    data = request.get_json()
    user_profile_sethandle_v1(data['token'], data['handle_str'])
    save_data_store()
    return dumps({})


@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    body = dm_create_v1(data['token'], data['u_ids'])
    save_data_store()
    return dumps({
        "dm_id": body["dm_id"]
    })


@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')

    body = dm_list_v1(token)
    return dumps({
        'dms': body['dms']
    })


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    dm_remove_v1(data['token'], data["dm_id"])
    save_data_store()
    return dumps({})


@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))

    body = dm_details_v1(token, dm_id)
    return dumps({
        "name": body["name"],
        "members": body["members"]
    })


@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    dm_leave_v1(data['token'], data["dm_id"])
    save_data_store()
    return dumps({})


@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    token = request.args.get('token')
    dm_id = int(request.args.get('dm_id'))
    start = int(request.args.get('start'))

    body = dm_messages_v1(token, dm_id, start)
    return dumps({
        "messages": body["messages"],
        "start": body["start"],
        "end": body["end"]
    })


@APP.route("/message/senddm/v1", methods=['POST'])
def message_senddm():
    data = request.get_json()
    body = message_senddm_v1(data["token"], data["dm_id"], data["message"])
    save_data_store()
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

@APP.route("/admin/user/remove/v1", methods=['DELETE'])
def admin_user_remove():
    body = request.get_json()
    admin_user_remove_v1(body['token'], body['u_id'])
    return dumps({})


@APP.route("/admin/userpermission/change/v1", methods=['POST'])
def admin_userpermission_change():
    body = request.get_json()
    admin_userpermission_change_v1(
        body['token'], body['u_id'], body['permission_id'])
    return dumps({})


@APP.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('', path)


@APP.route("/user/stats/v1", methods=["GET"])
def user_stats():
    token = request.args.get('token')

    body = user_stats_v1(token)
    return dumps({
        'user_stats': body['user_stats']
    })


@APP.route("/users/stats/v1", methods=["GET"])
def users_stats():
    token = request.args.get('token')

    body = users_stats_v1(token)
    return dumps({
        'workspace_stats': body['workspace_stats']
    })


@APP.route("/user/profile/uploadphoto/v1", methods=["POST"])
def user_profile_uploadphoto():
    data = request.get_json()

    user_profile_uploadphoto_v1(
        data['token'], data['img_url'], data['x_start'], data['y_start'], data['x_end'], data['y_end'])
    return dumps({})


@APP.route("/auth/passwordreset/request/v1", methods=['POST'])
def auth_passwordreset_request():
    body = request.get_json()
    email = body["email"]
    secret_code = auth_passwordreset_request_v1(email)
    if secret_code:
        reset_msg = Message(
            subject='Reset Code for UNSW Seams',
            sender=EMAIL_ADDRESS,
            recipients=[email],
            body=f"Your secret code to reset your password is {secret_code}.\n"
        )
        mail.send(reset_msg)

    return dumps({})


@APP.route("/auth/passwordreset/reset/v1", methods=['POST'])
def auth_passwordreset_reset():
    body = request.get_json()
    auth_passwordreset_reset_v1(
        body['reset_code'], body['new_password'])
    return dumps({})


@APP.route("/standup/start/v1", methods=['POST'])
def standup_start():
    data = request.get_json()
    body = standup_start_v1(data['token'], data['channel_id'], data['length'])
    return dumps({
        "time_finish": body['time_finish']
    })


@APP.route("/standup/active/v1", methods=['GET'])
def standup_active():
    token = request.args.get('token')
    channel_id = int(request.args.get('channel_id'))
    body = standup_active_v1(token, channel_id)
    return dumps({
        "is_active": body['is_active'],
        "time_finish": body['time_finish']
    })


@APP.route("/standup/send/v1", methods=['POST'])
def standup_send():
    data = request.get_json()
    body = standup_send_v1(data['token'], data['channel_id'], data['message'])
    return dumps(body)


@APP.route("/search/v1", methods=['GET'])
def search():
    token = request.args.get('token')
    query_str = request.args.get('query_str')
    body = search_v1(token, query_str)

    return dumps({
        "messages": body["messages"]
    })


@APP.route("/message/sendlater/v1", methods=['POST'])
def message_sendlater():
    body = request.get_json()
    data = message_sendlater_v1(
        body['token'], body['channel_id'], body['message'], body["time_sent"])
    save_data_store()
    return dumps({
        'message_id': data['message_id']
    })


@APP.route("/message/sendlaterdm/v1", methods=['POST'])
def message_sendlaterdm():
    body = request.get_json()
    data = message_sendlaterdm_v1(
        body['token'], body['dm_id'], body['message'], body["time_sent"])
    save_data_store()
    return dumps({
        'message_id': data['message_id']
    })


@APP.route("/message/share/v1", methods=['POST'])
def merssage_share():
    body = request.get_json()
    data = message_share_v1(body['token'], body['og_message_id'],
                            body["message"], body["channel_id"], body["dm_id"])
    save_data_store()
    return dumps({
        'shared_message_id': data['shared_message_id']
    })


@APP.route("/message/react/v1", methods=['POST'])
def message_react():
    body = request.get_json()
    message_react_v1(body['token'], body['message_id'], body["react_id"])
    save_data_store()
    return dumps({})


@APP.route("/message/unreact/v1", methods=['POST'])
def message_unreact():
    body = request.get_json()
    message_unreact_v1(body['token'], body['message_id'], body["react_id"])
    save_data_store()
    return dumps({})


@APP.route("/message/pin/v1", methods=['POST'])
def message_pin():
    body = request.get_json('token')
    message_pin_v1(body["token"], body["message_id"])
    save_data_store()
    return dumps({})


@APP.route("/message/unpin/v1", methods=['POST'])
def message_unpin():
    body = request.get_json('token')
    message_unpin_v1(body["token"], body["message_id"])
    save_data_store()
    return dumps({})


@APP.route("/notifications/get/v1", methods=['GET'])
def notifications_get():
    token = request.args.get('token')
    body = notifications_get_v1(token)
    return dumps({
        "notifications": body["notifications"]
    })

# wew14
# NO NEED TO MODIFY BELOW THIS POINT


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
