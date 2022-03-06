from src.data_store import data_store
from src.error import AccessError, InputError

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

def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
    store['channels'][channel_id]['channel_members'].append(auth_user_id)
    store['users'][auth_user_id]['channels_joined'].append(channel_id)
    return
