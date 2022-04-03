'''
data_store.py

This contains a definition for a Datastore class which you should use to store your data.
You don't need to understand how it works at this point, just how to use it :)

The data_store variable is global, meaning that so long as you import it into any
python file in src, you can access its contents.

Example usage:

    from data_store import data_store

    store = data_store.get()
    print(store) # Prints { 'names': ['Nick', 'Emily', 'Hayden', 'Rob'] }

    names = store['names']

    names.remove('Rob')
    names.append('Jake')
    names.sort()

    print(store) # Prints { 'names': ['Emily', 'Hayden', 'Jake', 'Nick'] }
    data_store.set(store)
'''
import re
import hashlib
# YOU SHOULD MODIFY THIS OBJECT BELOW

initial_object = {
    "users": {
        # auth_user_id : class object,
        # auth_user_id : class object
    },
    "channels": {
        # channel_id : class object,
        # channel_id : class object
    },
    "dms": {
        # dm_id : clas object,
        # dm_id : class object
    },
    "messages": {
        # message_id : clas object,
        # message_id : class object
    },
    "removed_users": {
        # channel_id : class object,
        # channel_id : class object
    }

}

# YOU SHOULD MODIFY THIS OBJECT ABOVE

# YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH


class Datastore:
    def __init__(self):
        self.__store = initial_object

    def get(self):
        return self.__store

    def set(self, store):
        if not isinstance(store, dict):
            raise TypeError('store must be of type dictionary')
        self.__store = store


print('Loading Datastore...')

global data_store
data_store = Datastore()


class User:

    def __init__(self, email, name_first, name_last, handle_str, password):
        self.u_id = self.set_u_id()
        self.permission_id = 0
        self.session_id = []  # double check if correct
        self.name_first = name_first
        self.name_last = name_last
        self.email = email
        self.handle_str = handle_str
        self.password = password
        self.channels_owned = []
        self.channels_joined = []
        self.messages_sent = []
        self.dms_own = []
        self.set_session_id()

    def set_u_id(self):
        try:
            store = data_store.get()
            return len(store['users']) + 1
        except:
            return 1

    def set_session_id(self):
        self.session_id.append(True)

    def set_permission_id(self):
        try:
            len(data_store.get()['users'])
            return 2
        except:
            return 1

    def check_session(self, session_id):
        return self.session_id[session_id]

    def add_ch_owned(self, ch_id, ch_object):
        self.channels_owned[ch_id] = ch_object

    def add_ch_joined(self, ch_id, ch_object):
        self.channels_joined[ch_id] = ch_object


class Base_channel:
    def __init__(self, auth_user_id, name, is_public):
        self.id = self.set_ch_id()
        self.name = name
        self.owner_members = []
        self.all_members = []
        self.message_list = []
        self.start = self.set_start()
        self.end = self.set_end()
        self.add_owner(auth_user_id)
        self.add_member(auth_user_id)

    def set_ch_id(self):
        try:
            store = data_store.get()
            return len(store['channels']) + 1
        except:
            return 1

    def add_owner(self, auth_user_id):
        store = data_store.get()
        self.owner_members[auth_user_id] = store["users"][auth_user_id]

    def add_member(self, auth_user_id):
        store = data_store.get()
        self.all_members[auth_user_id] = store["users"][auth_user_id]

    def set_start(self):
        return 0

    def set_end(self):
        return 50


class Channel(Base_channel):
    def __init__(self, is_public):
        self.is_public = is_public


class message:
    def __init__(self, message_id, u_id, message, time_sent, is_ch_message):
        self.message_id = message_id
        self.u_id = u_id
        self.message = message
        self.time_sent = time_sent
        self.is_ch_message = is_ch_message
