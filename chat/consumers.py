from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        self.room_id = self.scope['url_route']['kwargs']['slug']
        self.room_group_name = 'chat_%s' % self.room_id
        print("Channel '%s': user '%s' joined" % (self.room_id, self.user.username))

        # Join chat room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
    
        await self.accept()

    
    async def disconnect(self, close_code):
        # Leave the chat room
        await self.channel_layer.group_discard (self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data_json = json.loads(text_data)
        print(data_json)
        message = data_json['message']

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': self.user.username,
            }
        )
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        await self.send(text_data=json.dumps({
                'sender': sender,
                'message': message
            }))
