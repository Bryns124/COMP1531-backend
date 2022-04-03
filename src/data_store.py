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

# YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    "users" : {
        # auth_user_id : class object,
        # auth_user_id : class object
    },
    "channels" : {
        # channel_id : class object,
        # channel_id : class object
    },
    "dms" : {
        # dm_id : clas object,
        # dm_id : class object
    },
    "messages" : {
        # message_id : clas object,
        # message_id : class object
    },
    "removed_users" :{
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
