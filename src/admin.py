from src.error import InputError, AccessError



def admin_userpermission_change_v1(token, u_id, permission_id):
    store = datastore.get()

    auth_user_id = decode_token(token)["auth_user_id"]
    
    number_of_global_owners = 0
    user_exist = False
    for user in store['users']:
        if u_id == user['u_id']:
            user_exist = True
            target_user = user

        if auth_user_id == user['u_id']:
            auth_user = user

        if user['permission_id'] == 1:
            number_of_global_owners += 1
    
    valid_auth_user_id(auth_user_id)

    if auth_user["permission_id"] != 1:
        raise AccessError("You do not have permission for this command.")

    if not user_exist:
        raise InputError("The input u_id does not exist in the datastore.")

    if not permission_id in [1, 2]:
        raise InputError("Invalid permission id.")

    if target_user["permission_id"] == permission_id:
        raise InputError("User already has specified permissions")

    if (number_of_global_users < 2) & (permission_id = 2):
        raise InputError("Cannot demote only global user")

    for user in store["users"]:
        if user["u_id"] == u_id:
            user["permission_id"] = permission_id


def admin_user_remove_v1(token, u_id):

    auth_user_id = decode_token(token)["auth_user_id"]
    valid_auth_user_id(auth_user_id)

    store = data_store.get()

    number_of_global_owners = 0
    user_exist = False
    for user in store['users']:
        if u_id == user['u_id']:
            user_exist = True
            target_user = user

        if auth_user_id == user['u_id']:
            auth_user = user

        if user['permission_id'] == 1:
            number_of_global_owners += 1

    if auth_user["permission_id"] != 1:
        raise AccessError("The authorised user is not a global user.")

    if number_of_global_owners < 2:
        raise InputError("You cannot remove the only global owner.")

    remove_id_from_group(u_id, "channels")
    remove_id_from_group(u_id, "dms")
    
    i = 0
    for message in store["messages"]:
        if message["u_id"] == u_id:
            store["messages"][i]["message"] = "Removed user"
        i += 1

    removed_user = {
        "u_id": u_id
        "email": target_user["email"]
        "first_name": "Removed"
        "last_name": "user"
        "handle_str": target_user["handle_str"]   
    }
    store["removed_users"].append(removed_user)

    for user in store["users"]:
        if u_id == user["u_id"]:
            store["users"].remove(user)
        
    data_store.set(store)


def remove_id_from_group(u_id, group_type):
    '''
    Passes a u_id and either "channels" and "channel_id" or "dms" and "dm_id" for group_type 
    and group_id_string and a list of either channel_ids or dm_ids of which user is in. 
    Then removes u_id from each of the specified channels/dms owner/all members.
    '''

    store = data_store.get()

    i = 0
    for group in store[group_type]:
        if u_id in group["all_members"]:
            store[group_type][i]["all_members"].remove(u_id)
            if u_id in group["owner_members"]:
                store[group_type][i]["owner_members"].remove(u_id)
        i += 1

    data_store.set(store)
