from src.data_store import data_store
from src.error import InputError, AccessError

'''
    This function returns the list of dictionaries containing the details
    of the channels that the user is a member or owner of.
'''
def channels_list_v1(auth_user_id):
    store = data_store.get()

    for accounts in store['users']:
        if accounts['u_id'] == auth_user_id:
            output_list = create_list_dictionary(accounts)        
    return {
        'channels': output_list
    }

''' Helper function:
    Appends the list of dictionaries stored in the 'channels_owned' 
    and 'channels_joined' dictionaries in the data store, representing all
    the channels the user is associated with.
'''
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
    '''
    list all the channels that has been created

    Assumption: no access error AKA auth_user_id is valid
    returns: dictionary with a list of dictionaries of channels
    '''
    store = data_store.get()
    store_channels = store['channels']

    all_channels = []
    for channel in store_channels:
        channel_dict = {
        		'channel_id': channel['channel_id'],
        		'name': channel['channel_name'],
        	}
        all_channels.append(channel_dict)
    
    return {
        'channels': all_channels
    }


''' Function to create a new channel given the correct user id of a authorised user,
    the name of the channel and whether or not the channel is public or private. The return
    of this function is the id of that channel
'''
def channels_create_v1(auth_user_id, name, is_public):
    store = data_store.get()
    
    if len(name) > 20:
        raise InputError("The name of the channel cannot be more than 20 characters.")
    
    if len(name) < 1:
        raise InputError("The name of the channel cannot be less than 1 character.")
    
    if store == {}:
        new_channel_id = 1
    else:
        new_channel_id = len(store['channels']) + 1
    
    new_channel = {
        'channel_id' : new_channel_id, 
        'channel_name' : name,
        'is_public' : is_public,
        'owner_members' : [auth_user_id], 
        'all_members' : [auth_user_id],
        'messages' : [],
        'start' : 0, #ditto 
        'end' : 50,
    }
    
    for users in store['users']:
        if users['u_id'] == auth_user_id:
            users['channels_owned'].append(new_channel)
            
    store['channels'].append(new_channel)
    data_store.set(store)
    
    return {
        'channel_id' : store['channels'][-1]['channel_id']
    }

