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

redis_client = redis.Redis(host="redis", port="6379", db=1)

users_states = {}
users = {}
make_game = {}

class UserAccountSerializer(ModelSerializer):
    class Meta:
        model = UserAccount
        fields = ['id', 'first_name', 'last_name', 'avatar']

class TournamentConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        
        #check if the user joined already a tournament

        await self.accept()
        if self.scope['user'].is_authenticated is False:
            await self.send(json.dumps(
					{
						'error': 'Invalid Token'
					}
				))
			# await self.close()
            return
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]

        

        print("tournament id : " , tournament_id)

        
        self.group_name = f'tournament_{tournament_id}'
        # Add user to the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        ) 

        print("user id : ", self.scope['user'].id)
        max_len = int(redis_client.get("tournament_len").decode())

        if tournament_id >= max_len or tournament_id < 0:
            await self.send(text_data=json.dumps({
                    'error' : 'Tournament not found'
                }))
            await self.close()
            print("connection closed")
            return


        if tournament_id not in users:
            users[tournament_id] = []
            users_states[tournament_id] = {}
        
        users_states[tournament_id][self.scope['user'].id] = 1

        if (len(users[tournament_id]) == 8):
            await self.send(text_data=json.dumps({
                    'error' : 'Tournament is Full'
                }))
            return 

        for key, object_list in users.items():
            for obj in object_list:
                if obj.scope['user'].id == self.scope['user'].id:
                    await self.send(text_data=json.dumps({
                            'error' : 'User already joined an existing tournament'
                        }))
                    return 
        

        print("joined user : ", self.scope['user'].first_name)
        await self.channel_layer.group_send('notification',
                {
                    'type' : 'update_tournament',
                    'user_id' : self.scope['user'].id,
                    'id' : tournament_id,
                    'value' : 1,
                    'state' : 'connected'
                })
        
        users[tournament_id].append(self)
        # await sync_to_async(UserAccount.objects.filter(id=self.scope['user'].id).update)(user_state="in_game")
        self.scope['user'].user_state = "in_game"
        # user = await sync_to_async(UserAccount.objects.get)(id=self.scope['user'].id)

        # print("user state before", user.user_state)
        
        count = len(users[tournament_id])

        if count == 8:
        #    await self.send(text_data=json.dumps({'message' : 'Tournament is Full'}))
           print("before shuffling")
           for tournament in users[tournament_id]:
                print("user id : ", tournament.scope['user'].id)

           random.shuffle(users[tournament_id])
           print("after shuffling")

           for tournament in users[tournament_id]:
                print("user id : ", tournament.scope['user'].id)

           await self.channel_layer.group_send('notification',
            {
                'type' : 'generate_games',
                'nb_of_games' : 4,
                'tournament_group' : self.group_name,
                'user_id' : self.scope['user'].id,
                'last_user' : self.scope['user'].id

            })
           
           
           
    
    async def   match_making(self, event):
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
        listed_users = []
        indexes = event['games']
        i = 0
        j = 0

        
        if len(indexes) == 4:
            if self == users[tournament_id][0]:
                print("SEND USERS DATA TO ALL USERS")         
                # make_game[tournament_id]
                print(self.scope['user'])
                for user in users[tournament_id]:
                    serializer = UserSerializer(user.scope['user'])
                    listed_users.append(serializer.data)
                    if i == 2:
                        i = 0
                        j += 1

                    if i < 2:
                        await user.send(text_data=json.dumps(
                        {
                            'game_index' : indexes[j]
                        }   
                        ))
                    i += 1
                first_group = listed_users[:4]
                second_group = listed_users[4:]

                final_pairs = [(first_group), (second_group)]
                await self.channel_layer.group_send(self.group_name,
                    {
                        # 'users' : final_pairs
                        'type' : 'users_list',
                        'users' : final_pairs
                    })
        else:
            if self.scope['user'].id != event['last_user']:
                return 

            arr = []
            pos = make_game[tournament_id][self.scope['user'].id]
            for player in make_game[tournament_id]:
                if make_game[tournament_id][player] == pos:
                    arr.append(player)
                    #pop user from dictionary 
                
            
            if (len(arr) == 2):
                print(f"{self.scope['user'].last_name} IS READY TO PLAY")
                for user in users[tournament_id]: 
                    if (user.scope['user'].id == arr[0]) or (user.scope['user'].id == arr[1]):
                        serializer = UserSerializer(user.scope['user'])
                        listed_users.append(serializer.data)
                        await user.send(text_data=json.dumps(
                        {
                            'game_index' : indexes[0]
                        } ))
                await self.channel_layer.group_send(self.group_name,
                    {
                        # 'users' : final_pairs
                        'type' : 'users_list',
                        'users' : listed_users
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

        if len(winner_id) == 1 and users_states[tournament_id][winner_id] == 3:
            print("THE TOURNAMENT IS ENDED")
            users.pop(tournament_id)
            users_states[tournament_id][winner_id] += 1
            Tournament.create.objects(winner=winner_id)
            make_game.pop(tournament_id)
            await self.channel_layer.group_send('notification',
                {
                    'type' : 'update_tournament',
                    'user_id' : self.scope['user'].id,
                    'id' : tournament_id,
                    'value' : -8
                })
        elif len(winner_id) == 2:
            print("SEMI FINAL")
            users_states[tournament_id][winner_id[1]] += 1
            if tournament_id not in make_game:
                make_game[tournament_id] = {}
            make_game[tournament_id][winner_id[1]] = winner_id[0]
            print(make_game)
            # for player_pos in  make_game[tournament_id]:
            #     print("pos : ", make_game[tournament_id][player_pos])
            if len(make_game[tournament_id]) >= 2:
                i = 0
                for player_pos in  make_game[tournament_id]:
                    if  make_game[tournament_id][player_pos] == winner_id[0]:
                        i += 1

                if i == 2:
                    await self.channel_layer.group_send('notification',
                        {
                            'type' : 'generate_games',
                            'nb_of_games' : 1,
                            'tournament_group' : self.group_name,
                            'user_id' : self.scope['user'].id,
                            'last_user' : self.scope['user'].id
                        })

                    # generate_game

        else:
            users_states[tournament_id][winner_id] += 1

        await self.channel_layer.group_send(self.group_name,
            {
                'type' : 'send_winner',
                'winner' : [self.scope['user'].id, users_states[tournament_id][self.scope['user'].id]]
            })

        if len(winner_id) == 1 and users_states[tournament_id][winner_id] == 4:
            users_states.pop(tournament_id)
    
    async def 	send_winner(self, event):
        await self.send(text_data=json.dumps({
                'winner' : event['winner']
            }))

    async def	disconnect(self, code):

        # await sync_to_async(UserAccount.objects.filter(id=self.scope['user'].id).update)(user_state="offline")
        self.scope['user'].user_state = "offline"
        
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"] 

        if len(users[tournament_id]) < 8:
            print("User POPPED")

            users[tournament_id].remove(self)
            if len(users[tournament_id]) == 0:
                print("Tournament POPPED")
                users.pop(tournament_id)

            await self.channel_layer.group_send('notification',
                {
                    'type' : 'update_tournament',
                    'user_id' : self.scope['user'].id,
                    'id' : tournament_id,
                    'value' : -1,
                    'state' : 'disconnect'
                })

        print(f"user {self.scope['user'].last_name} is disconnected")
        await self.channel_layer.group_discard(self.group_name, self.channel_name)