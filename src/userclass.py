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
        return len(self.session_id) - 1 #session ids are starting at 2 for some reason

    def session_logout(self, session_id):
        self.session_id[session_id] = False #might be indexed wrong

    def check_session(self, session_id):
        return self.session_id[session_id]

    def set_permission_id(self):
        try:
            len(data_store.get()['users'])
            return 2
        except:
            return 1
