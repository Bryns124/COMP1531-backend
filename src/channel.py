from src.data_store import data_store
from src.error import InputError, AccessError



def channel_invite_v1(auth_user_id, channel_id, u_id):
    return {
    }

def channel_details_v1(auth_user_id, channel_id):
    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
        'all_members': [
            {
                'u_id': 1,
                'email': 'example@gmail.com',
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
                'handle_str': 'haydenjacobs',
            }
        ],
    }

def channel_messages_v1(auth_user_id, channel_id, start):
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
    }

'''
    Function to join and become a member of another channel,
    given that the channel exists and is not private.
    This function has no return
'''
def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
        
    if channel_validity(channel_id, store) == False:
        raise InputError("Channel id is invalid.")
    
    if already_member(auth_user_id, channel_id, store) == True:
        raise InputError("The user is already a member of this channel.")
    
    current_channel = extract_channel_details(channel_id, store)
    if current_channel['is_public'] == False:
        raise AccessError("This is a private channel, user does not have access.")


    for user_accounts in store['users']:
        if user_accounts['u_id'] == auth_user_id:
            new_member = user_accounts
            user_accounts['channels_joined'].append(current_channel)
    
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channels['all_members'].append(new_member)
            
    data_store.set(store)
    return

'''
    Helper function:
    to check if the channel id 
    input to channel_join funciton is valid and exists
    It return True if the id is valid and False otherwise.
'''
def channel_validity(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            return True
    return False

'''
    Helper function:
    to check if the user trying to join a new channel is 
    already a member of that channel.
    It returns True if the user is already a member and False otherwise
'''
def already_member(auth_user_id, channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id in channels['all_members'] or auth_user_id in channels['owner_members']:
                return True    
    return False

'''
    Helper function:
    to copy the channel details given a particular channel id
'''
def extract_channel_details(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channel_details = channels
    return channel_details
        
    
    
