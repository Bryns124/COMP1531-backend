import src.data_store
import src.channel

def channels_list_v1(auth_user_id):
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
    return 