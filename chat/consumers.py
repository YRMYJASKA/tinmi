from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
import re
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = 'chat_%s' % self.room_id
        self.last_msg_time = datetime.datetime.now()
    
        # Join chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    
        await self.accept()
         
        # Create a notification that an user joined
        infomsg = "User '%s' joined the room" % (self.user.username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'message': infomsg,
            }
        )
   
    
    async def disconnect(self, close_code):
        
        # Create a notification that an user left the channel
        infomsg = "User '%s' left the room" % (self.user.username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'notification_message',
                'message': infomsg,
            }
        )
        # Leave the chat room
        await self.channel_layer.group_discard (self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        print(data_json)
        message = data_json['message']
        
        # check if empty message, if so: disregard
        if len(message) < 1:
            return
        
        # Spam protection.          
        # If user sent their last message less than 0.5 second ago:  disregard
        curr_time = datetime.datetime.now()
        print((curr_time - self.last_msg_time).total_seconds())
        if (curr_time - self.last_msg_time).total_seconds() < 0.5:
            self.last_msg_time  = curr_time
            return 
        self.last_msg_time  = curr_time

        # Send the message to all current users in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
            }
        )
    async def chat_message(self, event):
        message_dirty = event['message']
        sender = event['sender']
        
        # Sanitize the string! AKA remove html tags
        cleanhtmlr = re.compile('<.*?>')
        message = re.sub(cleanhtmlr, '', message_dirty)

        await self.send(text_data=json.dumps({
                'sender': sender,
                'message': message,
                'type': 'user_msg'
            }))
    async def notification_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
                'message': message,
                'type': 'server_msg'
            }))
