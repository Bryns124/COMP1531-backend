import data_store
import channel

def channels_list_v1(auth_user_id):
    store = data_store.get()
    channel_list = {[]}
    
    for ids in store['users']:
        if (auth_user_id == ids['user_id']):
            channel_list.append(channel[ids])
            
    return channel_list


def channels_listall_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_create_v1(auth_user_id, name, is_public):
    store = data_store.get()
    store['channels']['name'].append(name)
    store['channels']['is_public'].append(is_public)
    
    channel_id = len(store['channels'][channel_id]) - 1
    store['channels']['channel_id'].append(channel_id)
    store['channels']['channel_owner'].append(auth_user_id)
    store['channels']['channel_members'].append([auth_user_id])
    store['channels']['channel_messages'].append([])
    
    data_store.set(store)
    
    channel_join_v1(auth_user_id, channel_id)
    
    return channel_id