from src.data_store import data_store
from src.error import AccessError, InputError
from src.channels import channels_list_v1

'''
channel_details_v1(auth_user_id, channel_id) 

returns (name, is_public, owner_members, all_members)

Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
'''

def channel_details_v1(auth_user_id, channel_id):
    store = data_store.get()

    is_channel = False
    is_member = False
    is_valid_u_id = False
    
    all_channels = store['channels']

    for user in store['users']:
        if user['u_id'] == auth_user_id:
            is_valid_u_id = True
            break
    
    if not is_valid_u_id:
        raise InputError("Invalid User ID")

    for channel in all_channels:
        if channel['channel_id'] == channel_id:
            is_channel = True
            active_channel = channel
            break
    
    if not is_channel:
        raise InputError()

    for member in active_channel['all_members']:
        if member == auth_user_id:
            is_member = True
            #break
        
    if not is_member:
        raise AccessError()

    return {
        'channel_name': active_channel['channel_name'],
        'is_public': active_channel['is_public'],
        'owner_members': active_channel['owner_members'],
        'all_members': active_channel['all_members']
    }

def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
    store['channels'][channel_id]['channel_members'].append(auth_user_id)
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


