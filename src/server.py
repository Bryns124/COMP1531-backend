from crypt import methods
import sys
import signal
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from src.error import InputError
from src import config, data_store
from src.auth import auth_login_v1, auth_register_v1
from src.other import clear_v1


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
    return dumps({
        'token': body['token'],
        'auth_user_id': body['auth_user_id']
    })


@ APP.route("/clear/v1", methods=['DELETE'])
def clear_v2():
    clear_v1()
    return dumps({

    })


@ APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })
# wew14
# NO NEED TO MODIFY BELOW THIS POINT


if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port, debug=True)  # Do not edit this port
