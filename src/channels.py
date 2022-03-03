import data_store
import channels


def channels_list_v1(auth_user_id):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

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
    new_channel_id = len(store['channels']['channel_id']) + 1
    
    new_channel = {
        'channel_id' : new_channel_id, 
        'channel_name' : name,
        'is_public' : is_public, #check if we can use None
        'owner_members' : [auth_user_id], #check again if this is leagal 
        'all_members' : [auth_user_id],
        'messages' : [],
        'start' : 0, #ditto 
        'end' : 50,
    }
    
    store['channels'].append(new_channel)
    data_store.set(store)
    
    return {
        store['channels'][-1]['channel_id']
    }
    # return {
    #     'channel_id': new_channel_id
    # }
