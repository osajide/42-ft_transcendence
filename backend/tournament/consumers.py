from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
import json
from asgiref.sync import sync_to_async
from authentication.serializers import UserSerializer
import random
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
import redis 
from collections import defaultdict

redis_client = redis.Redis(host="localhost", port="6379", db=1)

users_states = {}
users = {}

class UserAccountSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'first_name', 'last_name', 'avatar']

class TournamentConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):

        #check if tournament exists in the array and in the table

        #check if the user joined already a tournament

        await self.accept()
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]

        print("tournament id : " , tournament_id)


        tournament = await sync_to_async(Tournament.objects.filter(id=tournament_id).exists)()
        if tournament:
            await self.send(text_data=json.dumps({
                    'error' : 'you cannot join this tournament'
                }))
            return
        
        self.group_name = f'tournament_{tournament_id}'
        # Add user to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        ) 

        print("user id : ", self.scope['user'].id)
        max_len = int(redis_client.get("tournament_len").decode())

        if tournament_id >= max_len:
            await self.send(text_data=json.dumps({
                    'error' : 'Tournament not found'
                }))
            await self.close()
            print("connection closed")
            return

        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"] 
     
        if tournament_id not in users:
            users[tournament_id] = []
            users_states[tournament_id] = {}
            users_states[tournament_id][self.scope['user'].id] = 1

        if (len(users[tournament_id]) == 2):
            await self.send(text_data=json.dumps({
                    'message' : 'Tournament is Full'
                }))
            return 

        print("name : ", self.scope['user'].first_name)
        users[tournament_id].append(self.scope['user'])
        await sync_to_async(UserAccount.objects.filter(id=self.scope['user'].id).update)(user_state="in_game")
        self.scope['user'].user_state = "in_game"
        # user = await sync_to_async(UserAccount.objects.get)(id=self.scope['user'].id)

        # print("user state before", user.user_state)
        
        count = len(users[tournament_id])

        if count == 8:
        #    await self.send(text_data=json.dumps({'message' : 'Tournament is Full'}))
           for tournament in users[tournament_id]:
                print("user id : ", tournament.id)

           random.shuffle(users[tournament_id])
           print("after shuffling")

           for tournament in users[tournament_id]:
                print("user id : ", tournament.id)

           listed_users = []
           for user in users[tournament_id]:
                serializer = UserSerializer(user)
                listed_users.append(serializer.data)  

           first_group = listed_users[:4]
           second_group = listed_users[4:]

        #    first_pair = (first_group[0], first_group[1])
        #    second_pair = (first_group[2], first_group[3])

        #    third_pair = (second_group[0], second_group[1])
        #    fourth_pair = (second_group[2], second_group[3])

           final_pairs = [(first_group), (second_group)]

           await self.channel_layer.group_send(self.group_name,
            {
                # 'users' : final_pairs
                'type' : 'users_list',
                'users' : final_pairs
            })
    
    async def	users_list(self, event):
        await self.send(text_data=json.dumps({
                # 'users' : final_pairs
                'locked' : event['users']
                }))

    async def	receive(self, text_data=None, bytes_data=None):
        
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
        json_text_data = json.loads(text_data)

        winner_id = json_text_data["winner"]

        #check if the winner id is included in tha array first

        if winner_id is None:
             await self.send(text_data=json.dumps({
                'error' : 'winner id is not provided'
                }))

        print("winner id : ", winner_id)
        users_states[tournament_id][winner_id] += 1
        await self.channel_layer.group_send(self.group_name,
            {
                'type' : 'send_winner',
                'winner' : [self.scope['user'].id, users_states[tournament_id][self.scope['user'].id]]
            })
    
    async def 	send_winner(self, event):
        await self.send(text_data=json.dumps({
                'winner' : event['winner']
            }))

    async def	disconnect(self, code):

        await sync_to_async(UserAccount.objects.filter(id=self.scope['user'].id).update)(user_state="offline")
        self.scope['user'].user_state = "offline"
        
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"] 

        users[tournament_id].remove(self.scope['user'])
        users_states[tournament_id].pop(self.scope['user'].id)

        if len(users_states[tournament_id]) == 0:
            users_states.pop(tournament_id)

        if len(users[tournament_id]) == 0:
            users.pop(tournament_id)

        await self.channel_layer.group_send('notification',
            {
                'type' : 'update_tournament',
                'id' : tournament_id,
                'value' : -1
            })

        print(f"user {self.scope['user'].last_name} is disconnected")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)