from src.data_store import data_store

#resets all data from date_store to initial stage
def clear_v1():
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    data_store.set(store)
