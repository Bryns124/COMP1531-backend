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

    is_channel = False
    is_member = False
    
    all_channels = store['channels'] # Setting a list of all channels in data_store

    # Checking that the inputted channel_id is from a channel that exists
    for channel in all_channel:
        if channel['channel_id'] == channel_id:
            is_channel = True
            active_channel = channel # Saves the channel specified from channel_id
            break
    
    # Checking that the inputted user is in the channel specified
    for member in active_channel['all_members']:
        if member['u_id'] == auth_user_id:
            is_member = True
            break
        
    # Exceptions
    # If the inputted channel_id is not from a channel saved in data_store, raises an InputError
    if not is_channel:
        raise InputError()

    # If the inputted auth_user_id is not a member of the channel specified, raises an AccessError
    if not is_member:
        raise AccessError()

    # return a tuple (name, is_public, owner_members, all_members)
    return (active_channel['channel_name'], active_channel['is_public'], active_channel['owner members'], active_channel['all_members'])