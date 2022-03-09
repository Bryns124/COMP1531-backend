"""Contains clear function to clear datastore

clear: clears datastore
"""
from src.data_store import data_store

def clear_v1():
    """resets all data from data_store to initial stage

    Args: None

    Returns:
        empty dictionary: {} as this is the inital stage of data_store
    """
    store = data_store.get()
    store['users'] = []
    store['channels'] = []
    data_store.set(store)

    return {}
