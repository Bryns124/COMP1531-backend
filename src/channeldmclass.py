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

    def add_owner(self, auth_user_id):
        store = data_store.get()
        self.owner_members[auth_user_id] = store["users"][auth_user_id]
        data_store.set(store)

    def add_member(self, auth_user_id):
        store = data_store.get()
        self.all_members[auth_user_id] = store["users"][auth_user_id]
        data_store.set(store)

# class Dm(Parent):
#     def __init__(self, is_public):
#         self.is_public = is_public