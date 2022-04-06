from src.data_store import data_store


class User:
    def __init__(
        self, email, password, name_first, name_last, handle
    ):
        self.auth_user_id = self.set_u_id()
        self.permission_id = 0
        self.session_id = []  # double check if correct
        self.name_first = name_first
        self.name_last = name_last
        self.email = email
        self.handle = handle
        self.password = password
        self.channels_owned = {}    # Channels owned
        self.all_channels = {}  # Channels owned and joined
        self.messages_sent = {}
        self.dms_own = {}
        self.all_dms = {}  # ask
        self.set_session_id()  # fix later

    def set_u_id(self):
        try:
            store = data_store.get()
            return len(store['users']) + 1
        except:
            store = data_store.get()
            store["global_owners_count"] += 1
            return 1

    def set_session_id(self):
        self.session_id.append(True)
        # session ids are starting at 2 for some reason
        return len(self.session_id) - 1

    def session_logout(self, session_id):
        self.session_id[session_id] = False  # might be indexed wrong

    def check_session(self, session_id):
        return self.session_id[session_id]

    def add_ch_owned(self, ch_id, ch_object):
        self.channels_owned[ch_id] = ch_object

    def add_dm_owned(self, dm_id, dm_object):
        self.dms_own[dm_id] = dm_object

    def remove_dm_owned(self, dm_id):
        self.dms_own.pop(dm_id, None)

    def remove_ch_owned(self, ch_id):
        self.channels_owned.pop(ch_id, None)

    def add_channel(self, ch_id, ch_object):
        self.all_channels[ch_id] = ch_object

    def add_dm(self, dm_id, dm_object):
        self.all_dms[dm_id] = dm_object

    def add_msg(self, msg_id, message_object):
        self.messages_sent[msg_id] = message_object

    def channel_leave(self, ch_id):
        self.all_channels.pop(ch_id, None)
        self.channels_owned.pop(ch_id, None)

    def set_permission_id(self):
        try:
            len(data_store.get()['users'])
            return 2
        except:
            return 1

    # def set_session_id(self):
    #     self.session_id.append(True)


class Base:
    def __init__(self, auth_user_id, name):
        self.id = self.set_ch_id()
        self.name = name
        self.owner_members = {}
        self.all_members = {}
        self.message_list = []
        self.start = self.set_start()
        self.end = self.set_end()

    def set_ch_id(self):
        try:
            store = data_store.get()
            return len(store['channels']) + 1
        except:
            return 1

    def add_owner(self, auth_user_id, user_object):
        self.owner_members[auth_user_id] = user_object

    def remove_owner(self, auth_user_id):
        self.owner_members.pop(auth_user_id, None)

    def add_member(self, auth_user_id, user_object):
        self.all_members[auth_user_id] = user_object

    def user_leave(self, auth_user_id):
        self.all_members.pop(auth_user_id, None)
        self.owner_members.pop(auth_user_id, None)

    def set_start(self):
        return 0

    def set_end(self):
        return 50

    def get_type(self):
        store = data_store.get()
        if self.id in store['channels']:
            return "channel"
        elif self.id in store['dms']:
            return "dm"

    def check_msg_list(self, message_id):
        if message_id in self.message_list:
            return True
        else:
            return False


class Dm(Base):
    def __init__(self, auth_user_id, name,  u_ids):
        Base.__init__(self, auth_user_id, name)
        self.id = self.set_dm_id()

    def set_dm_id(self):
        try:
            store = data_store.get()
            return len(store['dms']) + 1
        except:
            return 1


class Channel(Base):
    def __init__(self, auth_user_id, name, is_public):
        Base.__init__(self, auth_user_id, name)
        self.is_public = is_public


class Message:
    def __init__(self, u_id, message, time_sent, parent):
        self.id = self.set_message_id()
        self.u_id = u_id
        self.message = message
        self.time_sent = time_sent
        self.parent = parent

    def set_message_id(self):
        store = data_store.get()
        if store['messages'] == {}:
            return 1
        else:
            return len(store['messages']) + 1

    def get_owner(self):
        return self.u_id

    def get_parent_type(self):
        return self.parent.get_type