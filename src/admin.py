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

    store = data_store.get()

    if u_id not in store["users"]:
        raise InputError("The user specified does not exist")

    if (store["global_owners_count"] == 1) and store["users"][u_id].permission_id == 1:
        raise InputError("You cannot remove the only global owner.")

    if not permission_id in [1, 2]:
        raise InputError("Invalid permission id.")

    if store["users"][u_id].permission_id == permission_id:
        raise InputError("User already has specified permissions")

    if store["users"][auth_user_id].permission_id != 1:
        raise AccessError("The authorised user is not a global user.")

    store["users"][u_id].permission_id = permission_id

    if permission_id == 1:
        store["global_users_count"] += 1

    if permission_id == 2:
        store["global_users_count"] -= 1

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

    store = data_store.get()

    if u_id not in store["users"]:
        raise InputError("The user specified does not exist")

    if (store["global_owners_count"] == 1) and store["users"][u_id].permission_id == 1:
        raise InputError("You cannot remove the only global owner.")

    if store["users"][auth_user_id].permission_id != 1:
        raise AccessError("The authorised user is not a global user.")

    store["users"][u_id].name_first = "Removed"
    store["users"][u_id].name_last = "user"
    messages_dict = store["users"][u_id].messages_sent

    for message in messages_dict:
        messages_dict[message].message = "Removed user"

    store["removed_users"][u_id] = store["users"].pop(u_id)

    data_store.set(store)

    return{}
