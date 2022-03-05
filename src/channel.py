from src.data_store import data_store
from src.error import AccessError, InputError

'''
channel_details_v1(auth_user_id, channel_id) 

returns (name, is_public, owner_members, all_members)

Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
'''
store = data_store.get()
def channel_details_v1(auth_user_id, channel_id):
    global store

    channel_members = []
    owner_members = []
    is_channel = False
    is_member = False
    
    all_channels = store['channels']

    for channel in all_channel:
        if channel['channel_id'] == channel_id:
            is_channel = True
            active_channel = channel
            break
    
    for member in active_channel['all_members']:
        if member['u_id'] == auth_user_id:
            is_member = True
            break
        
    if not is_channel:
        raise InputError() # fix this pls

    if not is_member:
        raise AccessError()

    return (active_channel['channel_name'], active_channel['is_public'], active_channel['owner members'], active_channel['all_members'])