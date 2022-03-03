from src.data_store import data_store
import src.channel

def channels_list_v1(auth_user_id):
    store = data_store.get()
    channel_list = []
    
    for accounts in store['users']:
        if auth_user_id == accounts['user_ids']:
            channel_list = accounts['channels_owned']
            channel_list += accounts['channels_joined']
            
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
    return 