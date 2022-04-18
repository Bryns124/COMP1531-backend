from base64 import decode
from src.data_store import data_store
from src.error import InputError, AccessError
from src.helper import decode_token, validate_token
from src.auth import email_check, duplicate_email_check
from urllib import request
import requests
import urllib.request
import sys
from PIL import Image, ImageFile
from src.config import port, url

BASE_URL = url
"""User has the 5 functions: users_all, user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle
Functions:
    users_all: Returns a list of all users and their associated details
    user_profile: For a valid user, return info on their user_id, email, first name, last name and handle
    user_profile_setname: Update the authorised user's first name and last name
    user_profile_setemail: Update the authorised user's email address
    user_profile_sethandle: Update the authorised user's hand (handle name)
    user_stats_v1: gives out data about the channels joined, dm joined and messages sent by the user and their involvement rate
    users_stats_v1: gives out data about the utilization of UNSW Seams
    user_profile_uploadphoto_v1: Allows user to upload their own profile pictures
"""


def users_all_v1(token):
    """returns a list of all users and their associated details

    Args:
        token (string): user calling the function

    Raises:
        None

    Returns:
        dictionary: containing list of dictionaries with the details of the users
    """
    store = data_store.get()
    decode_token(token)

    user_list = []
    for users in store['users']:
        user_list.append(extract_user_details(store["users"][users]))

    return {
        'users': user_list
    }


def extract_user_details(user):
    users = {
        'u_id': user.auth_user_id,
        'email': user.email,
        'name_first': user.name_first,
        'name_last': user.name_last,
        'handle_str': user.handle,
        'profile_img_url': user.profile_img_url
    }
    return users


def user_profile_v1(token, u_id):
    """returns a the details of one particular user with the associated user_id

    Args:
        token (string): user calling the function
        u_id (int): authorisation user id of the user whose details are required

    Raises:
        InputError: u_id does not refer to a valid user

    Returns:
        dictionary: containing the details of the user's profile
    """
    store = data_store.get()
    decode_token(token)
    valid_user_id(u_id)

    if u_id in store["removed_users"]:
        user_details = extract_user_details(store["removed_users"][u_id])
        return {'user': user_details}

    if u_id in store["users"]:
        user_details = extract_user_details(store["users"][u_id])

    return {
        'user': user_details
    }


def valid_user_id(user_id):
    """_summary_
    Validates that the input auth_user_id exists in the datastore
    Args:
        auth_user_id (u_id): The input u_id

    Raises:
        AccessError: If the u_id input does not exist in the system, an access error is raised.
    """
    store = data_store.get()

    if user_id in store["users"] or user_id in store["removed_users"]:
        return True

    raise InputError(
        description="This auth_user_id does not exist in the datastore.")


def user_profile_setname_v1(token, name_first, name_last):
    """Updates the authorised user's first and last name
    Args:
        token (string): user who wants their name changed in their profile

    Raises:
        InputError: length of first name is more than 50 character or less than 1 character
        InputError: length of first name is more than 50 character or less than 1 character

    Returns:
        None
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not name_length_check(name_first):
        raise InputError(
            description="The length of the new first name has to be within 1 and 50 characters inclusive")
    if not name_length_check(name_last):
        raise InputError(
            description="The length of the new last name has to be within 1 and 50 characters inclusive")

    store["users"][auth_user_id].name_first = name_first
    store["users"][auth_user_id].name_last = name_last
    data_store.set(store)
    return {}


def user_profile_setemail_v1(token, email):
    """Updates the authorised user's email
    Args:
        token (string): user who wants their email changed in their profile

    Raises:
        InputError: email does not follos valid email format
        InputError: email is already in use by another user

    Returns:
        None
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not valid_email(email):
        raise InputError(
            description="Email entered is not of valid format or is already in use by another user")

    store["users"][auth_user_id].email = email
    data_store.set(store)
    return {}


def user_profile_sethandle_v1(token, handle_str):
    """Updates the authorised user's handle name
    Args:
        token (string): user who wants their handle name changed in their profile

    Raises:
        InputError: length of handle name is not between 3 and 20 characters inclusive
        InputError: handle_str contains characters that are not alphanumeric
        InputError: the handle is already in use by another user

    Returns:
        None
    """
    store = data_store.get()
    auth_user_id = decode_token(token)['auth_user_id']

    if not valid_handle_string(store, handle_str):
        raise InputError(description="""
                         The length of the handle is between 3 and 20 characters,
                         or it contains non-alphanumeric characters,
                         or it is already in-use""")

    store["users"][auth_user_id].handle = handle_str
    data_store.set(store)
    return {}


def name_length_check(name):
    '''returns True if the length of the name is between 1 and 50 characters inclusive'''
    if len(name) > 50 or len(name) < 1:
        return False
    else:
        return True


def valid_email(email):
    '''returns True if the email follows proper email formatting and is not already in use by another user'''
    if not email_check(email) or duplicate_email_check(email):
        return False
    else:
        return True


def valid_handle_string(store, handle_str):
    '''returns True if all three of the following things are satisfied:
    - length is between 0 and 20 characters
    - is alphanumeric
    - not already in use
    '''
    if len(handle_str) > 20 or len(handle_str) < 3 or not handle_str.isalnum() or duplicate_handle(store, handle_str):
        return False
    else:
        return True


def duplicate_handle(store, handle_str):
    '''returns True if the given handle string is already use'''
    for users in store['users']:
        if handle_str == store["users"][users].handle:
            return True
    return False


def user_stats_v1(token):
    """returns the stats for a particular user about their user of UNSW Seams

    Args:
        token (string): user calling the function

    Raises:
        None

    Returns:
        user_stats (dictionary): containing list of dictionaries with the usage details of the users
    """
    auth_user_id = decode_token(token)['auth_user_id']

    channels_joined = generate_channels_joined_timed(auth_user_id)
    dms_joined = generate_dms_joined_timed(auth_user_id)
    messages_sent = generate_messages_sent_timed(auth_user_id)

    involvement_rate = calculate_ir(auth_user_id)

    user_stats = {
        "channels_joined": channels_joined,
        "dms_joined": dms_joined,
        "messages_sent": messages_sent,
        "involvement_rate": involvement_rate
    }
    return {
        "user_stats": user_stats
    }


def calculate_ir(auth_user_id):
    store = data_store.get()

    user_channels = len(store["users"][auth_user_id].all_channels)
    user_dms = len(store["users"][auth_user_id].all_dms)
    user_messages = len(store["users"][auth_user_id].messages_sent)

    numerator = sum([user_channels, user_dms, user_messages])
    denominator = sum([len(store["channels"]), len(store["dms"]), len(store["messages"])])

    if (numerator == 0 or denominator == 0):
        return 0

    involvement_rate = float(numerator) / float(denominator)

    if (involvement_rate > 1):
        return 1
    return involvement_rate


def generate_channels_joined_timed(auth_user_id):
    store = data_store.get()
    counter = 0
    channels_joined_list = [{
            "num_channels_joined": counter,
            "time_stamp": store["owner_timestamp"]
        }]

    all_channels = store["users"][auth_user_id].all_channels
    for channel in all_channels:
        counter += 1
        new_entry = {
            "num_channels_joined": counter,
            "time_stamp": all_channels[channel].time_created
        }
        channels_joined_list.append(new_entry)
    return channels_joined_list


def generate_dms_joined_timed(auth_user_id):
    store = data_store.get()
    counter = 0
    dms_joined_list = [{
            "num_dms_joined": counter,
            "time_stamp": store["owner_timestamp"]
        }]

    all_dms = store["users"][auth_user_id].all_dms
    for dm in all_dms:
        counter += 1
        new_entry = {
            "num_dms_joined": counter,
            "time_stamp": all_dms[dm].time_created
        }
        dms_joined_list.append(new_entry)
    return dms_joined_list


def generate_messages_sent_timed(auth_user_id):
    store = data_store.get()
    counter = 0
    messages_sent_list = [{
            "num_messages_sent": counter,
            "time_stamp": store["owner_timestamp"]
        }]

    messages_sent = store["users"][auth_user_id].messages_sent
    for message in messages_sent:
        counter += 1
        new_entry = {
            "num_messages_sent": counter,
            "time_stamp": messages_sent[message].time_sent
        }
        messages_sent_list.append(new_entry)
    return messages_sent_list




def users_stats_v1(token):
    """returns the stats related to the usage of UNSW Seams

    Args:
        token (string): user calling the function

    Raises:
        None

    Returns:
        users_stats (dictionary): containing list of dictionaries with the usage details of the website
    """
    decode_token(token)

    channels_exist = generate_channels_exist_timed()
    dms_exist = generate_dms_exist_timed()
    messages_exist = generate_messages_exist_timed()

    utilization_rate = calculate_utilization_rate()

    workspace_stats = {
        "channels_exist": channels_exist,
        "dms_exist": dms_exist,
        "messages_exist": messages_exist,
        "utilization_rate": utilization_rate
    }
    return {
        "workspace_stats": workspace_stats
    }

def calculate_utilization_rate():
    store = data_store.get()
    count = 0
    for user in store["users"]:
        if (len(store["users"][user].all_channels) != 0 or len(store["users"][user].all_dms) != 0):
            count += 1

    utilization_rate = float(count) / float(len(store["users"]))
    return utilization_rate


def generate_channels_exist_timed():
    store = data_store.get()
    counter = 0
    channel_exist = [{
            "num_channels_exist": counter,
            "time_stamp": store["owner_timestamp"]
        }]

    for channel in store["channels"]:
        counter += 1
        new_entry = {
            "num_channels_exist": counter,
            "time_stamp": store["channels"][channel].time_created
        }
        channel_exist.append(new_entry)
    return channel_exist

def generate_dms_exist_timed():
    store = data_store.get()
    counter = 0
    dm_exist = [{
            "num_dms_exist": counter,
            "time_stamp": store["owner_timestamp"]
        }]

    for dm in store["dms"]:
        counter += 1
        new_entry = {
            "num_dms_exist": counter,
            "time_stamp": store["dms"][dm].time_created
        }
        dm_exist.append(new_entry)
    return dm_exist

def generate_messages_exist_timed():
    store = data_store.get()
    counter = 0
    messages_exist = [{
            "num_messages_exist": counter,
            "time_stamp": store["owner_timestamp"]
        }]

    for message in store["messages"]:
        if message in store["removed_messages"]:
            continue
        counter += 1
        new_entry = {
            "num_messages_exist": counter,
            "time_stamp": store["messages"][message].time_sent
        }
        messages_exist.append(new_entry)
    return messages_exist


def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):
    """Allows users to upload their profile pictures using a url for their image

    Args:
        token (string): user calling the function
        img_url (string): url containing the image that the user wants to upload
        x_start (int): dimension to start cropping the image in the horizontal direction
        y_start (int): dimension to start cropping the image in the vertical direction
        x_end (int): dimension to finish cropping the image in the horizontal direction
        y_end (int):  dimension to finish cropping the image in the vertical direction

    Raises:
        InputError: url returns an HTTP status other than 200 or any other errors occur
        InputError: any of x_start, y_start, x_end, y_end are not within the dimensions of the image at the URL
        InputError: x_end is less than or equal to x_start or y_end is less than or equal to y_start
        InputError: image uploaded is not a JPG

    Returns:
        None
    """
    auth_user_id = decode_token(token)['auth_user_id']

    try:
        urllib.request.urlopen(img_url)
    except:
        raise InputError("Invalid image url") from InputError

    if (x_start > x_end or y_start > y_end):
        raise InputError("Invalid dimensions.")

    size = get_dimension(img_url)
    width = size[0]
    height = size[1]

    if (x_end > width or y_end > height):
        raise InputError("Invalid dimensions")

    if (not correct_format(img_url)):
        raise InputError("Only urls with jpg format are allowed")


    filename = f"./src/static/cropped_{auth_user_id}.jpg"
    store = data_store.get()
    urllib.request.urlretrieve(img_url, filename)

    crop_photo(filename, x_start, y_start, x_end, y_end)

    store["users"][auth_user_id].profile_img_url = BASE_URL + "static/cropped_" + str(auth_user_id) + ".jpg"
    data_store.set(store)
    return {}



def correct_format(img_url):
    img = Image.open(requests.get(img_url, stream=True).raw)

    if (img.format != 'JPEG'):
        return False
    return True


def crop_photo(filename, x1, y1, x2, y2):
    image = Image.open(filename)
    cropped_image = image.crop((x1, y1, x2, y2))
    cropped_image.save(filename)


def get_dimension(img_url):
    file = request.urlopen(img_url)
    p = ImageFile.Parser()
    while True:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return p.image.size

    file.close()
    return(None)
