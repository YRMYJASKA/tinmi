from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Chatroom
from .channel_commands import tinmi_commands 

import json
import re
import datetime
import random

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.user_group_name = 'user_%s' % self.user.username
        self.room_id = self.scope['url_route']['kwargs']['slug']
        self.theroom = Chatroom.objects.get(room_id=self.room_id)
        self.room_group_name = 'chat_%s' % self.room_id
        self.last_msg_time = datetime.datetime.now()
        self.colour = "#%06x" % random.randint(0, 0xFFFFFF)
        
        # Join chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
         
        # Create a notification that an user joined
        infomsg = "User '%s' joined the room" % (self.user.username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'server_message',
                'message': infomsg,
            }
        )

        # Add the user to the current user pool of the chat room
        self.theroom.current_users.append(self.user.username)
    
    async def disconnect(self, close_code):
        
        # Create a notification that an user left the channel
        infomsg = "User '%s' left the room" % (self.user.username)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'server_message',
                'message': infomsg,
            }
        )
        # Leave the chat room
        await self.channel_layer.group_discard (self.room_group_name, self.channel_name)

        # Delete user from current users
        self.theroom.current_users.remove(self.user.username)

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        print(data_json)
        message = data_json['message'].strip()
        
        # check if empty message, if so: disregard
        if len(message) < 1:
            return
        
        # Spam protection.          
        # If user sent their last message less than 0.5 second ago:  disregard
        curr_time = datetime.datetime.now()
        if (curr_time - self.last_msg_time).total_seconds() < 0.5:
            self.last_msg_time  = curr_time
            return 
        self.last_msg_time  = curr_time

        # Check if the message is some kind of command then execute
        # e.g '/ping', '/help'
        if message[0] == '/' and message.split(' ')[0][1:] in tinmi_commands.keys():
            # Echo the command back to the user but not to all the other people
            # Then execute the command itself
            await self.chat_message({'message': message, 'sender': self.user.username, 'colour': self.colour,})
            await tinmi_commands[message.split(' ')[0][1:]][0](message, self)
            return

        # Send the message to all current users in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
                'colour': self.colour,
            }
        )
    async def chat_message(self, event):
        message_dirty = event['message']
        sender = event['sender']
        colour = event['colour']

        # Sanitize the string! AKA remove html tags
        cleanhtmlr = re.compile('<.*?>')
        message = re.sub(cleanhtmlr, '', message_dirty)

        await self.send(text_data=json.dumps({
                'sender': sender,
                'message': message,
                'type': 'user_msg',
                'colour': colour
            }))
    async def server_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
                'message': message,
                'type': 'server_msg'
            }))
