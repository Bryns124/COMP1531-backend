1. Program will always receive an input 
2. Testing channel_create will always the first output channel id as 1 as we have to test on a fresh datastore. 
3. The IDs will be generated sequentially from 1.
4. When we create a new channel, messages will be empty.
5. When we join a channel, we will be able to see the message history for the channel.
6. Messages start value is equal to 0 in itteration 1. 
7. When creating a new channel, isPublic is set to None.
8. For the functions channel_create, channel_list, channel_listall, channel_details, channel_join, channel_messages,  which have auth_user_id as an argument, the user_id will always be valid.