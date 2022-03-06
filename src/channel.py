from src.data_store import data_store
from src.error import AccessError, InputError
from src.channels import channels_list_v1

'''
channel_details_v1(auth_user_id, channel_id) 

Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.

returns a dictionary 
{
    "channel_name": name of the channel (string),
    "is_public": whether or not the channel is public (boolean),
    "owner_members": a list of dictionaries containing owner users, each dictionary being of the form: {
        "u_id": user id (string),
        "email": email (string),
        "name_first": first name (string),
        "name_last": last name (string),
        "handle_str": user handle (string)
    }
    "all_members": a list of dictionaries in the same format as above, however containing information 
    on all members of the channel
}
'''


def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    
    auth_user_exist = False
    user_exist = False
    
    for user in store['users']:
        if auth_user_id == user['u_id']: 
            auth_user_exist = True
        elif u_id == user['u_id']:        
            user_exist = True
            
    if auth_user_exist == False or user_exist == False:
        raise InputError
    
    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True
            
    if channel_exist == False:
        raise InputError
        
    already_member = False
    can_invite = False
    for members in store['channels'][channel_id - 1]['all_members']:
        if members == u_id:
            already_member = True
        elif members == auth_user_id:
            can_invite = True
    
    if already_member == True:
        raise InputError
    
    if can_invite == False:
        raise AccessError
            
    for channel in store['channels']:
        for user in store['users']:
            if u_id == user['u_id']:
                invited_member = user['u_id']
                user['channels_joined'].append(channel)
        if channel["channel_id"] == channel_id: 
            channel['all_members'].append(invited_member)
        
            
    # print(store['channels'])
        
    data_store.set(store)
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    
    store = data_store.get() # Accessing data_store for data

    is_channel = False # Initialising booleans for raising errors
    is_member = False
    is_valid_u_id = False
    
    all_channels = store['channels'] # Saving list of channels as a local variable

    # Iterates over all users and checks if the provided user id is in the system
    for user in store['users']:
        if user['u_id'] == auth_user_id:
            is_valid_u_id = True # if the user id is found the boolean for valid user is set to True
    
    # if the user id is not in the system, raises an InputError
    if not is_valid_u_id: 
        raise InputError("Invalid User ID")

    # Iterates over all the channels and check if the provided channel id is in the system
    for channel in all_channels:
        if channel['channel_id'] == channel_id:
            is_channel = True # if the channel id is found the boolean for valid channel is set to True
            active_channel = channel # sets the given channel as active channel to use it later in the function
    
    # if the channel id is not in the system, raises an InputError
    if not is_channel:
        raise InputError("Invalid Channel ID")

    # Iterates over all members in the channel to check if the provided user id is a member of the channel
    for member in active_channel['all_members']:
        if member == auth_user_id:
            is_member = True # if the user is found in the channel, the boolean saving if the user is a channel member is set to True
    
    # if the user is not a member of the channel, raises an InputError
    if not is_member:
        raise AccessError()

    # initialising lists to save details about each owner/member respectively
    owner_members_details = []
    all_members_details = []

    # Iterates over every id in the list of owner members/all members respectively
    for owner_id in active_channel['owner_members']:
        # saves a dictionary containing details about a owner in owner_current and appends that to the list containing details 
        # about every owner
        owner_current = member_details(owner_id)
        owner_members_details.append(owner_current)

    for member_id in active_channel['all_members']:
        # does the same as previous but for all members
        # saves a dictionary containing details about a member in member_current and appends that to the list containing details
        # about every member
        member_current = member_details(member_id)
        all_members_details.append(member_current)
    
    # returns a dictionary with the format specified in the docstring for this function
    return {
        'channel_name': active_channel['channel_name'],
        'is_public': active_channel['is_public'],
        'owner_members': owner_members_details,
        'all_members': all_members_details
    }
'''
member_details(user_id)

Given a user_id returns a dictionary containing details regarding that user. Returns None if user is not in data_store.

returns a dictionary of the form: {
    "u_id": user id (string),
    "email": email (string),
    "name_first": first name (string),
    "name_last": last name (string),
    "handle_str": user handle (string)
}

'''
def member_details(user_id):
    store = data_store.get() # retrieves data from data_store
    users = store['users'] # saves list of dictionaries containing information about all users

    # iterates over all users and finds the user that matches the provided user_id
    for user in users:
        if user['u_id'] == user_id:
            # returns the required information in a dictionary specified in the docstring
            return {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle_str']
            }
    # returns None if user is not found, 
    return


def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
    store['channels'][channel_id - 1]['all_members'].append(auth_user_id)
    store['users'][auth_user_id]['channels_joined'].append(channel_id)
    return

def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    
    auth_user_exist = False
    user_exist = False
    
    for user in store['users']:
        if auth_user_id == user['u_id']: 
            auth_user_exist = True
        elif u_id == user['u_id']:        
            user_exist = True
            
    if auth_user_exist == False or user_exist == False:
        raise InputError
    
    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True
            
    if channel_exist == False:
        raise InputError
        
    already_member = False
    can_invite = False
    for members in store['channels'][channel_id - 1]['all_members']:
        if members == u_id:
            already_member = True
        elif members == auth_user_id:
            can_invite = True
    
    if already_member == True:
        raise InputError
    
    if can_invite == False:
        raise AccessError
            
    for channel in store['channels']:
        for user in store['users']:
            if u_id == user['u_id']:
                invited_member = user['u_id']
                user['channels_joined'].append(channel)
        if channel["channel_id"] == channel_id: 
            channel['all_members'].append(invited_member)
        
            
    # print(store['channels'])
        
    data_store.set(store)
    return {
    }