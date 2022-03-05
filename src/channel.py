from calendar import c
from email import message
from src.data_store import data_store
from src.channels import channels_list_v1
from src.error import AccessError, InputError

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
    store = data_store.get()
    
    # print(store)
    
    auth_user_exist = False
    
    for user in store['users']:
        if auth_user_id == user['u_id']: 
            auth_user_exist = True
    
    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True
        
    if channel_exist == False:
        raise InputError
    
    if len(store['channels'][channel_id - 1]['messages']) < start:
        raise InputError
        
    in_channel = False
  
    for members in store['channels'][channel_id -1]['all_members']:
        if members == auth_user_id:
                in_channel = True

    if in_channel == False:
        raise AccessError
    returned_messages = {'messages' : [], 'start': start, 'end': ""}
    returned_full = False
    for messages in store['channels'][channel_id - 1]['messages']:
        if messages['message_id'] >= start & messages['message_id'] < (start + 50):
            returned_messages['messages'].append(messages)
        elif messages['message_id'] == (start + 50):
            returned_full = True
    
    if returned_full == True:
        returned_messages['end'] = (start + 50)
    else:
        returned_messages['end'] = -1
    # print(returned_messages)

    return  returned_messages
    # {   
    #     'messages': [
    #         {
    #             'message_id': 1,
    #             'u_id': 1,
    #             'message': 'Hello world',
    #             'time_created': 1582426789,
    #         }
    #     ],
    #     'start': 0,
    #     'end': 50,
    # }

def channel_join_v1(auth_user_id, channel_id):
    return {
    }
