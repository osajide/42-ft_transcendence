from channels.generic.websocket import AsyncWebsocketConsumer
from .models import *
import json
from asgiref.sync import sync_to_async
from authentication.serializers import UserSerializer
import random
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
import redis 

redis_client = redis.Redis(host="redis", port="6379", db=1)

users_states = {}
users = {}
player_pos = {}

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
            await self.close()
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
            print("TOURNAMENT NOT FOUND")
            await self.send(text_data=json.dumps({
                    'error' : 'Tournament not found'
                }))
            await self.close()
            return


        if tournament_id not in users:
            users[tournament_id] = []
            users_states[tournament_id] = {}
        
        users_states[tournament_id][self.scope['user'].id] = 1

        if (len(users[tournament_id]) == 8):
            print('error : Tournament is Full')
            await self.send(text_data=json.dumps({
                    'error' : 'Tournament is Full'
                }))
            await self.close()
            return 

        
        user = await sync_to_async(UserAccount.objects.get)(id=self.scope['user'].id)
        if user.user_state == "in_game":
            print("user already in game")
            await self.send(text_data=json.dumps({
                    'error' : 'User already joined an existing tournament'
                }))
            await self.close()
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
        await sync_to_async(UserAccount.objects.filter(id=self.scope['user'].id).update)(user_state="in_game")
        self.scope['user'].user_state = "in_game"
        
        count = len(users[tournament_id])

        if count == 8:
            print("before shuffling")
            for tournament in users[tournament_id]:
                    print("user id : ", tournament.scope['user'].id)

            random.shuffle(users[tournament_id])
            print("after shuffling")

            for tournament in users[tournament_id]:
                    print("user id : ", tournament.scope['user'].id)
            
            listed_users = []

            for user in users[tournament_id]:
                serializer = UserSerializer(user.scope['user'])
                listed_users.append(serializer.data)
            first_group = listed_users[:4]
            second_group = listed_users[4:]

            final_pairs = [(first_group), (second_group)]
            await self.channel_layer.group_send(self.group_name,
                {
                    # 'users' : final_pairs
                    'type' : 'users_list',
                    'users' : final_pairs,
                })
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
        indexes = event['games']
        i = 0
        j = 0

        print("MATCH MAKING")
        print("===================================> indexes : ", indexes)
        if len(indexes) == 4:
            if self == users[tournament_id][0]:
                print("SEND USERS DATA TO ALL USERS")         
                print(self.scope['user'])
                for user in users[tournament_id]:
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
        else:
            if self.scope['user'].id != event['last_user']:
                return 
            print("the user who make game : ", event['last_user'])

            arr = []
            if users_states[tournament_id][self.scope['user'].id] == 2:
                print("user id : ", self.scope['user'].id)
                print("matches len : ", len(player_pos[tournament_id]))
                print("winners array : ", player_pos[tournament_id])
                id = self.scope['user'].id
                pos = player_pos[tournament_id].get(id)
                if pos is None:
                    print("POSITON NOT VALID")
                else:
                    print("player pos : ", player_pos[tournament_id].get(id))
                for player_idx in player_pos[tournament_id]:
                    if (player_pos[tournament_id].get(player_idx) == pos) and (users_states[tournament_id][player_idx] == users_states[tournament_id][self.scope['user'].id]):
                        print(f"player index {player_idx} in position {player_pos[tournament_id][player_idx]}")
                        arr.append(player_idx)
                
            elif users_states[tournament_id][self.scope['user'].id] == 3: 
                print("MAKE FINAL GAME")
                for user in users_states[tournament_id]:
                    if users_states[tournament_id][user] == 3:
                        print("id of player that reach final => ", user)
                        arr.append(user)
            
            if (len(arr) == 2):
                print('Rak hna: ', self.scope['user'].id)
                listed_users = []
                for user in users[tournament_id]: 
                    if (user.scope['user'].id == arr[0]) or (user.scope['user'].id == arr[1]):
                        print(f"{user.scope['user'].last_name} IS READY TO PLAY")

                        serializer = UserSerializer(user.scope['user'])
                        listed_users.append(serializer.data)
                        await user.send(text_data=json.dumps(
                        {
                            'game_index' : indexes[0]
                        } ))
                # await self.channel_layer.group_send(self.group_name,
                #     {
                #         # 'users' : final_pairs
                #         'type' : 'users_list',
                #         'users' : listed_users
                #     })
                
    

    async def	users_list(self, event):
        
        if 'state' in event:
            state = event["state"]
            if state == "disconnect":
                print("========= USER CLOSE CONNECTION IN TOURNAMENT END")
                await self.close()
                return

        
        
        await self.send(text_data=json.dumps({
                # 'users' : final_pairs
                'locked' : event['users']
                }))

    async def	receive(self, text_data=None, bytes_data=None):
        
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"]
        json_text_data = json.loads(text_data)

        winner_id = json_text_data["winner"]

        #check if the winner id is included in tha array first
        i = 0

        if winner_id is None:
            await self.send(text_data=json.dumps({
                'error' : 'winner id is not provided'
                }))
            return
        
        if self.scope['user'].id != winner_id[1]:
            return 

        print("winner id : ", winner_id)
        print("user scope id : ", self.scope['user'].id)
        
       
        # print("SEMI FINAL")
        if tournament_id not in player_pos:
            player_pos[tournament_id] = {}
        
        
        if winner_id[1] not in player_pos[tournament_id]:
            player_pos[tournament_id][winner_id[1]] = winner_id[0]
            print(f"SET PLAYER {self.scope['user'].id} POSITION ", player_pos[tournament_id][winner_id[1]])

        users_states[tournament_id][winner_id[1]] += 1
        if users_states[tournament_id][winner_id[1]] == 4:
            print("TOURNAMENT WINNER : ", winner_id[1])
        print("winner : ", [winner_id[1],  users_states[tournament_id][winner_id[1]]])  
        if len(player_pos[tournament_id]) > 1:

            players = []
            
            print("PLAYERS STAGES ============= ", users_states[tournament_id])
            print("PLAYERS POSITIONS ============= ", player_pos[tournament_id])
            
            if users_states[tournament_id][winner_id[1]] == 3:
                print("FINALS CHECK ", self.scope['user'].id)
                for player in  player_pos[tournament_id]:
                    if users_states[tournament_id][player] == 3:
                        players.append(player)
                        i += 1
                if (i == 2):
                    print("FINAAAAAL")
                    
            else:
                for player in  player_pos[tournament_id]:
                    print(f"player position : {player_pos[tournament_id][player]} , and player id {player}")

                    if (player_pos[tournament_id][player] == winner_id[0]) and tournament_id in users_states and (users_states[tournament_id][player] == users_states[tournament_id][winner_id[1]]):
                        print(f"MATCHED PLAYER {player} THAT HAS {users_states[tournament_id][player] - 1} WINS")
                        players.append(player)
                        i += 1
                
        
        await self.channel_layer.group_send(self.group_name,
            {
                'type' : 'send_winner',
                'game_winner' : [winner_id[1],  users_states[tournament_id][winner_id[1]], winner_id[0]]
            })
        
        if i == 2:
            print(f"IN RECEIVE == MAKE GAME BEETWEN {players[0]} , count {users_states[tournament_id][players[0]]} ,, and {players[1]} , count {users_states[tournament_id][players[1]]}")
            print(f"last action by {self.scope['user'].id}")
            await self.channel_layer.group_send('notification',
                {
                    'type' : 'generate_games',
                    'nb_of_games' : 1,
                    'tournament_group' : self.group_name,
                    'user_id' : self.scope['user'].id,
                    'last_user' : self.scope['user'].id
                })
            
        if users_states[tournament_id][winner_id[1]] == 4:
            print("TOURNAMENT WINNER : ", winner_id[1])
            users.pop(tournament_id)
            if tournament_id not in users:
                print("TOURNAMENT POPPED WHEN TOURNAMENT ENDS")
            else:
                print("TOURNAMENT NOT POPPED")
            await sync_to_async(Tournament.objects.create)(winner=winner_id[1])
            del player_pos[tournament_id]
            del users_states[tournament_id]
            await self.channel_layer.group_send(self.group_name,
                {
                    # 'users' : final_pairs
                    'type' : 'users_list',
                    'state' : 'disconnect'
                })
            print("TOURNAMENT ENDED")
            print("RESET TOURNAMENT")
            await self.channel_layer.group_send('notification',
                {
                    'type' : 'update_tournament',
                    'user_id' : self.scope['user'].id,
                    'id' : tournament_id,
                    'value' : -8,
                    'state' : 'disconnect'
                })
    
    async def 	send_winner(self, event):
        await self.send(text_data=json.dumps({
                'winner' : event['game_winner']
            }))

    async def	disconnect(self, code):

        await sync_to_async(UserAccount.objects.filter(id=self.scope['user'].id).update)(user_state="offline")
        self.scope['user'].user_state = "offline"
        
        tournament_id = self.scope["url_route"]["kwargs"]["tournament_id"] 

       


        
        if tournament_id in users_states and self.scope['user'].id in users_states[tournament_id]:
            users_states[tournament_id].pop(self.scope['user'].id, None)
        if tournament_id in users and self in users[tournament_id]:
            users[tournament_id].remove(self)
            print("POPPED USER OBJECT FROM TOURNAMENT")
        if tournament_id in users and len(users[tournament_id]) == 0:
            print("Tournament POPPED")
            users.pop(tournament_id)
            users_states.pop(tournament_id)
            await self.channel_layer.group_send('notification',
                {
                    'type' : 'update_tournament',
                    'user_id' : self.scope['user'].id,
                    'id' : tournament_id,
                    'value' : -8,
                    'state' : 'disconnect'
                })
            
        if tournament_id in users and (len(users[tournament_id]) > 0 and len(users[tournament_id]) < 8):
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