from src.helper import decode_token, generate_token

u_id = 1
class User:

    def __init__(
        self, session_id, password, permission_id,
        email, name_first, name_last, channels, dms, messages_sent, handle
    ):
        global u_id


        self.__auth_user_id = u_id
        self.__session_id = session_id
        self.__password = password
        self.__permission_id = permission_id
        self.__email = email
        self.__name_first = name_first
        self.__name_last = name_last
        self.__channels = channels
        self.__dms = dms
        self.__messages_sent = messages_sent
        self.__handle = handle

        u_id += 1

    def setname(self, new_name_first, new_name_last):
        self.__name_first = new_name_first
        self.__name_last = new_name_last

    def setemail(self, new_email):
        self.__email = new_email

    def sethandle(self, new_handle):
        self.__handle = new_handle