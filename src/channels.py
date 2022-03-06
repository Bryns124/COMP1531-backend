from src.data_store import data_store
import src.channels
from src.error import InputError, AccessError
from src.channel import channel_join_v1

store = data_store.get()

def channels_list_v1(auth_user_id):
    store = data_store.get()

    for accounts in store['users']:
        if accounts['u_id'] == auth_user_id:
            output_list = create_list_dictionary(accounts)        
    return {
        'channels': output_list
    }

def create_list_dictionary(accounts):
    output_list = []
    for owned in accounts['channels_owned']:
            channel = {
                'channel_id': owned['channel_id'],
                'channel_name': owned['channel_name']
            }
            output_list.append(channel)
        
    for joined in accounts['channels_joined']:
        channel = {
            'channel_id': joined['channel_id'],
            'channel_name': joined['channel_name']
        }
        output_list.append(channel)
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
    store = data_store.get()
    
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
    
    for users in store['users']:
        if users['u_id'] == auth_user_id:
            users['channels_owned'].append(new_channel)
            
    store['channels'].append(new_channel)
    #this might be the issue to the whole problem
    # channel_join_v1(auth_user_id, new_channel['channel_id'])
    data_store.set(store)
    
    return {
        'channel_id' : store['channels'][-1]['channel_id']
    }
    

