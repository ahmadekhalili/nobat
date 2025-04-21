from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def update_browser_status(statuses):
    # Sending message to WebSocket group (room)
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'room_browser_status_room',
        {
            'type': 'send_status_update',
            'statuses': statuses,
        }
    )
