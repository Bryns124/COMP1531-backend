1. Program will always receive an input 
2. Invalid User ID will not be input 
3. Testing channel_create will always the first output channel id as 1 as we have to test on a fresh datastore. 
4. The IDs will be generated sequentially from 1.
5. When we create a new channel, messages will be empty.
6. When we join a channel, we will be able to see the message history for the channel.
7. Messages start value is equal to 0. 
8. When creating a new channel, isPublic is set to None.
9. For the functions requiring auth_user_id as an argument, the user_id will always be valid.
