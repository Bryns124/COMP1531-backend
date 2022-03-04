from src.data_store import data_store
from src.channels import channels_list_v1
from src.error import AccessError, InputError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    store = data_store.get()
    
    for user in store['users']:
        if auth_user_id != user['u_id']: 
            raise InputError
        elif u_id != user['u_id']:        
            raise InputError
    
    for channel in store['channels']:
        if channel['channel_id'] != channel_id:
            raise InputError
        
        
    for members in channels_list_v1['all_members']:
        if members['u_id'] == u_id:
            raise InputError
        if members['u_id'] != auth_user_id:
            raise AccessError    
        
    for user in store['users']:
        if auth_user_id == user['u_id']:
            invited_member = user
    
    for channel in store['channels']:
        if channel["channel_id"] == channel_id: 
            channel['all_members'].append(invited_member)
        
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
    return {
    }
