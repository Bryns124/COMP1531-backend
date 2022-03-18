<<<<<<< HEAD
from data_store import data_store

def messages_send_v1(token, channel_id, message):
    pass
=======
from src.data_store import data_store

def message_send_v1(token, channel_id, message):
    pass
#{message_id}

def message_edit_v1(token, message_id, message):
    store = data_store.get()

    for message in store['messages']:
        if message['message_id'] == message_id:
            message['message'] == message

    data_store.set(store)

    return {}
#{}
def message_remove_v1(token, message_id):
    store = data_store.get()

    for message in store['messages']:
        if message['message_id'] == message_id:
            if (message['is_cnanel']):


    data_store.set(store)
    return {}
#{}

def do message_remove(message_id):
    for channel in store['channels']:
>>>>>>> 02b8f6c1cc0e2056ccf9d5e672eedff383aca26e
