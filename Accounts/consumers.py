# chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Profile, Message


def _room_name_from_profiles(a_id, b_id):
    a, b = sorted([str(a_id), str(b_id)])
    return f"private_chat_{a}_{b}"


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.other_slug = self.scope["url_route"]["kwargs"].get("slug")

        # Use sync_to_async for DB access
        try:
            self.user_profile = await sync_to_async(Profile.objects.get)(user=user)
            self.other_profile = await sync_to_async(Profile.objects.get)(slug=self.other_slug)
        except Profile.DoesNotExist:
            await self.close(code=4004)
            return

        # Create deterministic room name
        self.room_name = _room_name_from_profiles(self.user_profile.id, self.other_profile.id)
        self.room_group_name = f"chat_{self.room_name}"

        # Join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"✅ {user.username} connected to {self.room_group_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"❌ Disconnected from {self.room_group_name}")

    async def receive(self, text_data=None, bytes_data=None):
        if not text_data:
            return

        data = json.loads(text_data)
        msg_text = data.get("message", "").strip()
        if not msg_text:
            return

        # Save message asynchronously
        msg = await sync_to_async(Message.objects.create)(
            sender=self.user_profile,
            recipient=self.other_profile,
            content=msg_text,
        )

        # Fetch sender data safely inside sync_to_async
        user_data = await sync_to_async(lambda: {
            "username": self.user_profile.user.username,
            "first_name": self.user_profile.user.first_name or self.user_profile.user.username
        })()

        payload = {
            "type": "chat_message",  # ✅ must match async def chat_message
            "id": msg.id,
            "message": msg.content,
            "sender": user_data["username"],
            "sender_first": user_data["first_name"],
            "timestamp": msg.timestamp.isoformat(),
        }

        # Broadcast the message
        await self.channel_layer.group_send(self.room_group_name, payload)
        print(f"📤 Message broadcast to {self.room_group_name}: {msg_text}")

    async def chat_message(self, event):
        print("💬 chat_message triggered:", event)
        await self.send(text_data=json.dumps({
            "id": event.get("id"),
            "message": event.get("message"),
            "sender": event.get("sender"),
            "sender_first": event.get("sender_first"),
            "timestamp": event.get("timestamp"),
        }))
