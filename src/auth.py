from operator import truediv
import re
from src.data_store import data_store
from src.error import InputError
import jwt
from src.helper import generate_token, decode_token, generate_secret_code
import hashlib
from src.classes import User
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import change_pw_email.txt

EMAIL_ADDRESS = "w17a.ant@gmail.com"
EMAIL_PASSWORD = """BirdsAren'tReal"""


def auth_login_v1(email, password):
    """
    Logs in a registered user given an email and password

    :param email: the user's email
    :param password: the user's password
    :return: token, u_id
    """
    users = data_store.get()["users"]
    for u_id in users:
        if users[u_id].email == email and users[u_id].password == hash_password(password):
            return {
                "token": generate_token(u_id),
                "auth_user_id": u_id
            }
        elif users[u_id].email == email and users[u_id].password != hash_password(password):
            raise InputError(description="Password is incorrect")

    raise InputError(description="Email does not exist")


def auth_register_v1(email, password, name_first, name_last):
    if not email_check(email):
        raise InputError(description="Email entered is not a valid email")
    if duplicate_email_check(email):
        raise InputError(
            description="Email entered has already been registered")
    if len(password) < 6:
        raise InputError(
            description="Password entered must be longer than 6 characters")
    if len(name_first) < 1 or len(name_first) > 50:
        raise InputError(
            description="First name entered must be between 1 and 50 characters inclusive")
    if len(name_last) < 1 or len(name_last) > 50:
        raise InputError(
            description="Last name entered must be between 1 and 50 characters inclusive")

    handle = create_handle(name_first, name_last)
    new_user = User(
        email, hash_password(password), name_first, name_last, handle
    )
    store = data_store.get()
    store["users"][new_user.auth_user_id] = new_user
    data_store.set(store)

    u_id = int(new_user.auth_user_id)
    return {
        "token": generate_token(u_id),
        "auth_user_id": u_id
    }


def auth_logout_v1(token):
    """_summary_
    Logs the user off, removing their current session_id from the datastore.
    Args:
        token (string): token of user, obtained when logging on or when registering.
    """

    u_id = decode_token(token)['auth_user_id']
    s_id = decode_token(token)['session_id']
    store = data_store.get()

    store["users"][u_id].session_logout(s_id)
    data_store.set(store)

    return {}


def auth_passwordreset_request_v1(email):
    # Considering writing most of this in server??
    # Very broken atm
    store = data_store.get()

    # return None if email not in data_store
    if not duplicate_email_check(email):
        return None

    target_user = identify_user_from_email(email)

    secret_code = generate_secret_code()  # generate_secret_code not written yet

    store["users"][target_user.u_id].secret_code = secret_code
    store["users"][target_user.u_id].session_id = []

    context = ssl.create_default_context()

    s = smtplib.SMTP(host="smtp.gmail.com", port=465)
    s.starttls()
    s.login(EMAIL_ADDRESS, EMAIL_ADDRESS)

    msg = MIMEMultipart()
    email_template = read_template('change_pw_email.txt')
    # check names are okay
    email_contents = email_template.substitute(
        NAME_FIRST=target_user.name_first, NAME_LAST=target_user.name_last, SECRET_CODE=secret_code)

    msg['From'] = EMAIL_ADDRESS
    msg['To'] = email
    msg['Subject'] = 'UNSW Seams - Password Change Request'

    msg.attach(MIMEText(email_contents, 'plain'))

    s.send_message(msg)
    s.quit()

    # sign out of email

    data_store.set(store)


def auth_passwordreset_reset_v1(reset_code, new_password):
    store = data_store.get()
    target_user = identify_user_from_reset_code(reset_code)
    if target_user == None:
        raise InputError(description="Reset code invalid")

    if len(new_password) < 6:
        raise InputError(
            description="Password entered must be longer than 6 characters")

    store["users"][target_user.u_id].password = hash_password(new_password)
    store["users"][target_user.u_id].secret_code = None

    data_store.set(store)


def identify_user_from_email(email):
    store = data_store.get()

    for u_id in store["users"]:
        if store["users"][u_id].email == email:
            return store["users"][u_id]


def identify_user_from_reset_code(code):
    store = data_store.get()

    for u_id in store["users"]:
        if store["users"][u_id].reset_code == code:
            return store["users"][u_id]


########################################
###### - - HELPER FUNCTIONS - - #######
######################################

def email_check(email):
    """
    Checks if the email entered is valid.

    :email: the user's email
    :return: whether the email is valid or not
    :rtype: boolean
    """
    regex = re.compile(
        r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
    return bool(re.fullmatch(regex, email))


def hash_password(password):
    """_summary_
    Encodes the password given when registering.
    Args:
        password (string): Users input plantext password.

    Returns:
        string: Hashed password
    """
    return hashlib.sha256(password.encode()).hexdigest()


def duplicate_email_check(email):
    """
    Checks if the email entered has already been registered.

    :email: the user's email
    :return: whether the email is new or already has been registered
    :rtype: boolean
    """
    store = data_store.get()
    if store["users"] == {}:
        return False
    for user in store['users']:
        if store["users"][user].email == email:
            return True
    return False


def create_handle(name_first, name_last):
    """
    Creates the user's handle with the first name and last name.
    If the user's handle is more than 20 characters, it is cut off at 20 characters
    If the user's handle already exists, append the handle with the smallest number
    (starting from 0).

    :name_first: the user's first name
    :name_last: the user's last name
    :return: the user's handle
    :rtype: string
    """
    store = data_store.get()

    handle = name_first.lower() + name_last.lower()
    handle = ''.join(filter(str.isalnum, handle))
    handle = handle[:20]

    i = 0
    for user in store['users']:
        if store['users'][user].handle == handle:
            if i == 0:
                handle += str(0)
                i += 1
                continue
            if i == 10:
                handle = handle[:-1] + str(i)
                i += 1
                continue
            if i % 10 == 1 and i > 10:
                handle = handle[:-2] + str(i)
                i += 1
                continue
            if i % 10 == 0:
                handle = handle[:-2] + str(i)
                i += 1
                continue
            handle = handle[:-1] + str(i % 10)
            i += 1

    return handle
