import data_store

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

def channel_join_v1(auth_user_id, channel_id):
    store = data_store.get()
    
    if channel_join_validity(channel_id) == True:
        for user_accounts in store['users']:
            if user_accounts['u_id'] == auth_user_id:
                new_member = user_accounts
                user_accounts['channels_joined'].append(extract_channel_details(channel_id))
    
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channels['all_members'].append(new_member)
            
    data_store.set(store)
    return

def channel_join_validity(channel_id):
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel_id and channels['is_public'] == True:
            return True
        
    return False

def extract_channel_details(channel_id):
    store = data_store.get()
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channel_details = channels
    return channel_details
        
    
    
