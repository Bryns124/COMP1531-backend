from src.data_store import data_store
import datetime
from datetime import timezone
# from src.helper import generate_timestamp
from src.config import port, url
import time
import threading

BASE_URL = url

def generate_timestamp():
    """
    Generates the times_sent for messages.
    Returns:
        int: Type cast int of the current utc timestamp.
    """
    time = datetime.datetime.now(timezone.utc)
    utc = time.replace(tzinfo=timezone.utc)
    timestamp = utc.timestamp()
    return int(timestamp)



class User:
    def __init__(
        self, email, password, name_first, name_last, handle
    ):
        self.auth_user_id = self.set_u_id()
        self.permission_id = self.set_permission_id()
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
        self.profile_img_url = f"{BASE_URL}/static/default.jpg"
        self.set_session_id()  # fix later
        self.reset_code = None
        self.notifications = []

    def set_u_id(self):
        store = data_store.get()
        return len(store['users']) + len(store['removed_users']) + 1

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

    def dm_leave(self, dm_id):
        self.all_dms.pop(dm_id, None)
        self.dms_own.pop(dm_id, None)

    def set_permission_id(self):
        if len(data_store.get()['users']) == 0:
            store = data_store.get()
            store['global_owners_count'] += 1
            return 1
        else:
            return 2
    # def set_session_id(self):
    #     self.session_id.append(True)

    # def event_in_channel(self, ch_id):
    #     if ch_id in self.all_channels:
    #         return ch_id
    #     else:
    #         return -1

    # def event_in_dm(self, dm_id):
    #     if dm_id in self.all_dms:
    #         return dm_id
    #     else:
    #         return -1


class BaseChannel:
    def __init__(self, auth_user_id, name):
        self.id = self.set_ch_id()
        self.name = name
        self.owner_members = {}
        self.all_members = {}
        self.message_list = []
        self.start = self.set_start()
        self.end = self.set_end()

    def set_ch_id(self):
        store = data_store.get()
        return len(store['channels']) + 1

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
        else:
            return "dm"

    # def check_msg_list(self, message_id):
    #     if message_id in self.message_list:
    #         return True
    #     else:
    #         return False


class Dm(BaseChannel):
    def __init__(self, auth_user_id, name,  u_ids):
        BaseChannel.__init__(self, auth_user_id, name)
        self.id = self.set_dm_id()
        self.time_created = generate_timestamp() #for the user and users stats

    def set_dm_id(self):
        store = data_store.get()
        return len(store['dms']) + 1

    def remove_all(self):
        # try:
        for member in self.owner_members:
            self.owner_members[member].dm_leave(self.id)
            # self.owner_members.pop(member, None)
            # self.all_members.pop(member, None)
        # except:
        #     pass
        for member in self.all_members:
            # try:
            self.all_members[member].dm_leave(self.id)
            # self.all_members.pop(member, None)
            # except:
            #     pass


class Standup:
    def __init__(self, auth_user_id, parent_channel, length):
        self.owner = auth_user_id
        self.start_time = int(time.time())
        self.end_time = int(time.time() + length)
        self.parent_channel = parent_channel
        self.message = ""
        self.session = self.start_session(length)

    def start_session(self, length):
        # not tested
        # if length == 0:
        #     t = threading.Timer(2, self.parent_channel.reset_standup())
        #     t.start()
        #     return False
        # else:
        t = threading.Timer(length, self.end_session)
        t.start()
        return True
        # while time.time() < self.end_time:
        #     return True
        # return False

    def end_session(self):
        self.session = False
        self.parent_channel.end_standup()

    def message_compile(self, auth_user_id, message):
        user_str = self.parent_channel.all_members[auth_user_id].handle
        if self.message == "":
            self.message = f"{user_str}: {message}"
        else:
            self.message = self.message + '\n' + f"{user_str}: {message}"

    def message_send(self):
        if self.message == "":
            return
        store = data_store.get()
        new_message = Message(self.owner, self.message,
                              self.end_time, self.parent_channel)
        store['messages'][new_message.id] = new_message
        store['users'][self.owner].add_msg(new_message.id, new_message)
        self.parent_channel.message_list.append(new_message.id)



class Channel(BaseChannel):
    def __init__(self, auth_user_id, name, is_public):
        BaseChannel.__init__(self, auth_user_id, name)
        self.is_public = is_public
        self.time_created = int(generate_timestamp()) #for the user and users stats
        self.active_standup = None

    def start_standup(self, auth_user_id, duration):
        self.active_standup = Standup(auth_user_id, self, duration)

    def end_standup(self):
        self.active_standup.message_send()
        self.reset_standup()

    def reset_standup(self):
        self.active_standup = None


class Message:
    def __init__(self, u_id, message, time_sent, parent):
        self.id = self.set_message_id()
        self.u_id = u_id
        self.message = message
        self.time_sent = time_sent
        self.parent = parent
        self.is_pinned = False
        self.react_id = 0
        self.react_ud_ids = []

    def set_message_id(self):
        store = data_store.get()
        if store['messages'] == {}:
            return 1
        else:
            return len(store['messages']) + 1

    def get_owner(self):
        return self.u_id

    def get_parent_type(self):
        return self.parent.get_type()

    def react(self, u_id):
        self.react_id = 1
        self.react_ud_ids.append(u_id)

    def unreact(self, u_id):
        self.react_ud_ids.remove(u_id)
        if len(self.react_ud_ids) == 0:
            self.react_id = 0

    def is_user_reacted(self, u_id):
        if u_id in self.react_ud_ids:
            return True
        return False
