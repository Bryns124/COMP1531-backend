from src.data_store import data_store
from src.error import AccessError, InputError

def channel_invite_v1(auth_user_id, channel_id, u_id):
    """
    Allows a authorized user to invite another user to a channel they are apart of.

    Args:
        auth_user_id (u_id): A valid user who is apart of the channel/
        channel_id (channel_id): The channel id auth_user is inviting to.
        u_id (u_id): A valid second user who is being invited

    Raises:
        InputError: u_id dos not exist in datastore.
        InputError: channel_id does not exist in datastore.
        InputError: the invited user is already part of the channel.
        AccessError: the auth_user is not in the channel they are inviting to.

    Returns:
        dictionary: nothing! nothing is returned after a invite 
    """
    store = data_store.get()
    
    auth_user_exist = False
    user_exist = False
    
    for user in store['users']:
        if auth_user_id == user['u_id']: 
            auth_user_exist = True
        elif u_id == user['u_id']:        
            user_exist = True
            
    if auth_user_exist == False or user_exist == False:
        raise InputError
    
    channel_exist = False
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_exist = True
            
    if channel_exist == False:
        raise InputError
        
    already_member = False
    can_invite = False
    for members in store['channels'][channel_id - 1]['all_members']:
        if members == u_id:
            already_member = True
        elif members == auth_user_id:
            can_invite = True
    
    if already_member == True:
        raise InputError
    
    if can_invite == False:
        raise AccessError
            
    for channel in store['channels']:
        for user in store['users']:
            if u_id == user['u_id']:
                invited_member = user['u_id']
                user['channels_joined'].append(channel)
        if channel["channel_id"] == channel_id: 
            channel['all_members'].append(invited_member)
        
            
    # print(store['channels'])
        
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
    """_summary_
    Taking a valid uesr it pulls a list of up to 50 messages from a starting point and returns them. 
    Args:
        auth_user_id (_u_id): The valid id of the user calling the messages.
        channel_id (channel_id): The channel_id of the channel which to call the messages from.
        start (int): A starting index value.

    Raises:
        InputError: u_id does not exist in data store.
        InputError: channel_id does not exist in data store.
        InputError: the starting index is greater than the messages in the channel.
        AccessError: u_id does not have access to the channel 

    Returns:
        _type_: _description_
    """
    store = data_store.get()
    
    # print(store)
    
    auth_user_exist = False
    
    for user in store['users']:
        if auth_user_id == user['u_id']: 
            auth_user_exist = True
    
    if auth_user_exist == False:
        raise InputError
    
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
    '''
    function allows user to join another channel based on the channel ID
    will give input error if the channel id is invalid or if the user is already in the channel
    will give access error if the channel ID is one for a private channel
    '''
    store = data_store.get()
        
    if channel_validity(channel_id, store) == False:
        raise InputError("Channel id is invalid.")
    
    if already_member(auth_user_id, channel_id, store) == True:
        raise InputError("The user is already a member of this channel.")
    
    current_channel = extract_channel_details(channel_id, store)
    if current_channel['is_public'] == False:
        raise AccessError("This is a private channel, user does not have access.")


    for user_accounts in store['users']:
        if user_accounts['u_id'] == auth_user_id:
            new_member = user_accounts
            user_accounts['channels_joined'].append(current_channel)
    
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channels['all_members'].append(new_member)
            
    data_store.set(store)
    return


def channel_validity(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            return True
    return False


def already_member(auth_user_id, channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            if auth_user_id in channels['all_members'] or auth_user_id in channels['owner_members']:
                return True    
    return False


def extract_channel_details(channel_id, store):
    for channels in store['channels']:
        if channels['channel_id'] == channel_id:
            channel_details = channels
    return channel_details    

