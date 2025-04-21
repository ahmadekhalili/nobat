from channels.generic.websocket import AsyncWebsocketConsumer
import json

class BrowserStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"cunsomer connect")
        self.room_name = 'browser_status_room'
        self.room_group_name = f'room_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        pass

    # Send status update to WebSocket
    async def send_status_update(self, event):
        print(f"cunsomer send_status_update. event received: {event}")
        statuses = event['statuses']  # Get the status updates
        await self.send(text_data=json.dumps({
            'statuses': statuses
        }))

