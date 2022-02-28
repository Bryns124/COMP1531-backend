
# functions to test: channel_details_v1, channel_join_v1

# Assumed that channel ids have form 30001, leading 3
# Assumed that user ids have form 20005, leading 2 
'''
channel_details_v1(auth_user_id, channel_id) 

returns (name, is_public, owner_members, all_members)

Given a channel with ID channel_id that the authorised user is a member of, provide basic details about the channel.
'''

# fixtures
def test_channel_details_v1():
# Chunk of preset lists imitating actual lists of info, eg. lists of all users, channels etc

    # Couple of test users, honestly idk
    user0000 = {
        "u_id" = 20000
        "email" = "danielyung@web.com"
        "name_first" = "Daniel"
        "name_last" = "Yung"
        "handle_str" = "danielyung"
    }
    user0001 = {
        "u_id" = 20001
        "email" = "geoffreyzhu@web.com"
        "name_first" = "Geoffrey"
        "name_last" = "Zhu"
        "handle_str" = "geoffreyzhu"
    }

    # Assume channel_list_master is a list of channels with each element being a tuple of the form
    # (channel_id, name, is_public, member_list)
    channel_list_master = [
    (30000, "general", True, [user0000, user0001]),
    (30001, "admin", False, [user0000])
    (30002, "muted", True, [user0001])
    (30003, "private", False, [])
    (30004, "other", True, [user0000])
    ]
    chan0 = {
        "channel_id" = 30000
        "name" = "general"
    }
    chan1 = {
        "channel_id" = 30001
        "name" = "admin"
    }
    chan2 = {
        "channel_id" = 30002
        "name" = "muted"
    }
    

    # Should spit InputError when channel_id does not refer to a valid channel
    assert channel_details_v1(20000, 30003) == InputError

    # Should spit AccessError when channel_id is valid and the authorised user is not a member of the channel
    assert channel_details_v1(20000, 30002) == AccessError

    # Error for when auth_user_id is invalid
    assert channel_details_v1(20002, 30001) == InvalidUser

    # Standard Tests for correct inputs
    assert channel_details_v1(20000, 30000) == ("general", True, [user0000], [user0000, user0001])
    assert channel_details_v1(20001, 30000) == ("general", True, [user0000], [user0000, user0001])
    assert channel_details_v1(20000, 30001) == ("admin", False, [user0000], [user0000])
    assert channel_details_v1(20001, 30002) == ("muted", True, [], [user0001])

'''
channel_join_v1(auth_user_id, channel_id)

returns None

Given a channel_id of a channel that the authorised user can join, adds them to that channel.
'''
# Assumed that all users can join a public channel and that owners can join any channel

def test_channel_join_v1():
    # Spits InputError when channel_id does not refer to a valid channel or the authorised user is already a member of the channel
    assert channel_join_v1(20000, 30011) == InputError
    assert channel_join_v1(20000, 30000) == InputError

    # Spits AccessError when channel_id refers to a channel that is private and the authorised user is not already a channel member 
    # and is not a global owner
    assert channel_join_v1(20001, 30001) == AccessError

    # Standard tests for correct input
    # Test that users can join public channels
    channel_join_v1(20000, 30002)
    assert user0000 in channel_details_v1(20000, 30002)[3]

    # Test that owners can join any channel
    channel_join_v1(20001, 30004)
    assert user0001 in channel_details_v1(20001, 30004)[3]