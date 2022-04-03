from src.data_store import data_store
from src.userclass import User


class Channel():
    def __init__(
        self, auth_user_id, name, is_public
    ):
        self.channel_id = self.set_ch_id()
        self.name = name
        self.is_public = is_public
        self.owner_members = {}
        self.all_members = {}
        self.messages = {}

    def set_ch_id(self):
        try:
            store = data_store.get()
            return len(store['channels']) + 1
        except:
            return 1

    def add_owner(self, auth_user_id, user_object):
        self.owner_members[auth_user_id] = user_object

    def remove_owner(self, auth_user_id):
        remove = self.owner_members.pop(auth_user_id, None)

    def add_member(self, auth_user_id, user_object):
        self.all_members[auth_user_id] = user_object

    def user_leave(self, auth_user_id):
        leave_all = self.all_members.pop(auth_user_id, None)
        leave_owner = self.owner_members.pop(auth_user_id, None)

# class Dm(Parent):
#     def __init__(self, is_public):
#         self.is_public = is_public