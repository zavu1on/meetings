from json import loads, dumps
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser

users = {}


class RoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        tokens = self.scope['url_route']['kwargs']

        if self.scope['user'] == AnonymousUser:
            return await self.disconnect(-1)

        self.room_group_name = f'{tokens["token1"]}-{tokens["token2"]}'

        if self.room_group_name not in users.keys():
            users[self.room_group_name] = []

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'enter',
                'data': {'id': self.scope['user'].id},
            }
        )

        await self.accept()

    async def disconnect(self, close_code):
        u = list(filter(lambda el: el['id'] == self.scope['user'].id, users[self.room_group_name]))[0]
        users[self.room_group_name].remove(u)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'move',
                'users': users[self.room_group_name],
            }
        )

    async def receive(self, text_data):
        json = loads(text_data)

        if json['type'] == 'move':
            if json['data']['id'] not in map(lambda el: el['id'], users[self.room_group_name]):
                users[self.room_group_name].append(json['data'])
            else:
                users[self.room_group_name] = list(
                    map(lambda el: json['data'] if el['id'] == json['data']['id'] else el, users[self.room_group_name]))

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'move',
                    'users': users[self.room_group_name],
                }
            )
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send.sdp',
                    'data': json,
                }
            )

    async def move(self, event):
        await self.send(dumps({
            'users': event['users']
        }))

    async def send_sdp(self, event):
        receive = event['data']
        await self.send(dumps(receive))

    async def enter(self, event):
        receive = event['data']
        await self.send(dumps({
            **receive,
            'type': 'enter'
        }))
