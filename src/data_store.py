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

## YOU SHOULD MODIFY THIS OBJECT BELOW
initial_object = {
    #'users': [
        # {
            # 'u_id' : , check if is ok 
            # 'email': "", check if using empty string is ok 
            # 'name_first': "", 
            # 'name_last': "", 
            # 'handle_str': "" , 
            # 'password': "",
            # 'channels_owned' : [], 
            # 'channels_joined' : [],
        # }
    #],
    #'channels': [
        # {
        #     'channel_id' : , 
        #     'channel_name' : "",
        #     'is_public' : None, #check if we can use None
        #     'owner_members' : ['users'], #check again if this is leagal 
        #     'all_members' : ['users'],
        #     'messages' : [
        #         {
        #             'message_id' : , #similarly check if legal
        #             'u_id' : , 
        #             'message': "",
        #             'time_created': ,
        #         }
        #     ],
        #     'start' : , #ditto 
        #     'end' : , 

        # }
    #],
}

## YOU SHOULD MODIFY THIS OBJECT ABOVE

## YOU ARE ALLOWED TO CHANGE THE BELOW IF YOU WISH
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
