from src.data_store import data_store
import src.channels
from src.error import InputError, AccessError

store = data_store.get()

def channels_list_v1(auth_user_id):
    global store
    store = data_store.get()
    channel_list = []
    output_list = []
    
    for accounts in store['users']:
        if auth_user_id == accounts['u_id']:
            channel_list = accounts['channels_owned']
            channel_list += accounts['channels_joined']
            
    for channels in channel_list:
        temp_channel_dict = {
            'channel_id': channels['channel_id'],
            'channel_name': channels['channel_name']
        }
        output_list.append(temp_channel_dict)
        
    return output_list



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
    global store
    
    if len(name) > 20:
        raise InputError("The name of the channel cannot be more than 20 characters.")
    
    if len(name) < 1:
        raise InputError("The name of the channel cannot be less than 1 character.")

    new_channel_id = len(store['channels']) + 1
    
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
        'channel_id' : store['channels'][-1]['channel_id']
    }
    

