from src.error import InputError, AccessError
from src.helper import valid_auth_user_id, decode_token
from src.data_store import data_store


def admin_userpermission_change_v1(token, u_id, permission_id):
    """
    admin_userpermission_change_v1

    Given a user by their user ID, set their permissions to new permissions described by
    permission_id.

    InputError when: u_id is invalid, u_id is the only global user and is being demoted,
    permission_id in invalid or the user already has the permission_id requested.

    AccessError when the authorised user is not a global owner.

    Input: {token, u_id, permission_id}
    Output: {}
    """
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

    if not user_exist:
        raise InputError("The input u_id does not exist in the datastore.")

    if auth_user["permission_id"] != 1:
        raise AccessError("You do not have permission for this command.")

    if not permission_id in [1, 2]:
        raise InputError("Invalid permission id.")

    if target_user["permission_id"] == permission_id:
        raise InputError("User already has specified permissions")

    if (number_of_global_owners < 2) & (permission_id == 2):
        raise InputError("Cannot demote only global user")

    i = 0
    for user in store["users"]:
        if user["u_id"] == u_id:
            store["users"][i]["permission_id"] = permission_id
        i += 1

    data_store.set(store)


def admin_user_remove_v1(token, u_id):
    '''
    admin_user_remove

    Given a user by their u_id, remove them from the Seams. They are removed from all channels/DMs,
    and will not be included in the list of users returned by users/all. Removed users have the contents
    of their messages changed to 'Removed user'. Their profile is still retrievable with user/profile,
    with: name_first: 'Removed', name_last: 'user'. The user's email and handle should be reusable.

    InputError when u_id is invalid or u_id is the only global owner
    AccessError when the authorised user is not a global owner

    Input: {token, u_id}
    Output: {}
    '''
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

    if not user_exist:
        raise InputError("The user specified does not exist")

    if auth_user["permission_id"] != 1:
        raise AccessError("The authorised user is not a global user.")

    if (number_of_global_owners < 2) and (target_user["permission_id"] == 1):
        raise InputError("You cannot remove the only global owner.")

    remove_id_from_group(u_id, "channels")
    remove_id_from_group(u_id, "dms")

    i = 0
    for message in store["messages"]:
        if message["u_id"] == u_id:
            store["messages"][i]["message"] = "Removed user"
        i += 1

    removed_user = {
        "u_id": u_id,
        "email": target_user["email"],
        "name_first": "Removed",
        "name_last": "user",
        "handle_str": target_user["handle_str"]
    }
    store["removed_users"].append(removed_user)

    for user in store["users"]:
        if u_id == user["u_id"]:
            store["users"].remove(user)

    data_store.set(store)

    return{}


def remove_id_from_group(u_id, group_type):
    '''
    Receives a u_id and either "channels" or "dms" for group_type.

    Then removes u_id from each of the specified channels/dms owner/all members.

    Input: {u_id, group_type, (group_type is a string of either "channels" or "dms")}
    Output: {}
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

    return{}
