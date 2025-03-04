from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Game
import json
import random
from authentication.models import UserAccount
from authentication.serializers import UserSerializer
import redis
from django.db.models import Q
import asyncio 

redis_client = redis.Redis(host='redis', port=6379, db=1)

games = {}

@sync_to_async
def	create_game_record(self, stats):
	score1 = stats['loser']['score']
	score2 = stats['winner']['score']
	mode = stats['mode']

	if games[self.game_id]['host'].user.id == stats['winner']['id']:
		score1 = stats['winner']['score']
		score2 = stats['loser']['score']

	Game.objects.create(
		game_type=mode,
		player1=games[self.game_id]['host'].user,
		player2=games[self.game_id]['opponent'].user,
		player1_score=score1,
		player2_score=score2,
		winner=stats['winner']['id']
	)

def	generate_ball_directions():
		directions = []
		for _ in range(22):
				x = random.randint(-20, 20)
				while x >= -10 and x <= 10:
						x = random.randint(-20, 20)

				y = random.randint(-20, 20)
				while y >= -10 and y <= 10:
						y = random.randint(-20, 20)
				directions.append({
						'x': x,
						'y': y
				})
		return directions

class	GameConsumer(AsyncWebsocketConsumer):
	async def	connect(self):
		await self.accept()

		self.user = self.scope['user']
		self.game_id = self.scope['url_route']['kwargs']['id']

		if redis_client.exists('max_games') == False:
			redis_client.set('max_games', 0)

		max_game_id = int(redis_client.get('max_games').decode())
		
		if self.game_id >= max_game_id:
			await self.send(text_data=json.dumps({'error': f'Invalid game id: {self.game_id}'}))
			await self.close(code=4000)

		if self.user.is_authenticated == False:
			await self.send(text_data=json.dumps({'error': 'user not authenticated'}))
			await self.close(code=4000)
			return

		print("IN CONNECT === game id ====>", self.game_id)
		if not self.game_id in games:
			games[self.game_id] = {}
			games[self.game_id]['disconnected'] = []

		self.group_name = f'{self.game_id}'

		await self.channel_layer.group_add(self.group_name, self.channel_name)
		print(f"game before host and opponent: {games}, game id : {self.game_id}")
		if 'host' in games[self.game_id] and games[self.game_id]['host'].user is not self.user: # not the same user trying to connect twice
			print(f"this is the opponent of the game {self.scope['user']}") 
			games[self.game_id]['opponent'] = self
			games[self.game_id]['ready'] = 0
			await self.channel_layer.group_send(self.group_name,
								{
									'type': 'broadcast',
									'locked': True
								})

			await games[self.game_id]['host'].send(text_data=json.dumps(
				{
					'opponent': UserSerializer(games[self.game_id]['opponent'].user).data
				}
			))
			await games[self.game_id]['opponent'].send(text_data=json.dumps(
				{
					'view': -1,
					'opponent': UserSerializer(games[self.game_id]['host'].user).data
				}
			))
		else:
			print(f'this is the host of the game {self.scope["user"]}') 
			games[self.game_id]['host'] = self
		

	async def	receive(self, text_data=None, bytes_data=None):
		json_text_data = json.loads(text_data)

		# if 'stats' in json_text_data:
		# 	print(f'You have received stats from : {self.user}')
		if 'w' and 'h' and 'mobile' in json_text_data:
			await self.channel_layer.group_send(self.group_name,
									   {
										   'type': 'send_aspect',
										   'aspect' : json_text_data,
										   'id': self.user.id
									   })

		elif 'key' in json_text_data:
			await self.channel_layer.group_send(self.group_name,
									   {
										   'type': 'broadcast',
										   'key' : json_text_data['key'],
										   'id': self.user.id
									   })
			
		elif 'ready' in json_text_data:
			games[self.game_id]['ready'] += 1
			if games[self.game_id]['ready'] == 2: 
				ball_initial_directions = generate_ball_directions()
				await self.channel_layer.group_send(self.group_name,
										{
											'type': 'broadcast',
											'start': ball_initial_directions
										})
		elif 'stats' in json_text_data and self.game_id in games:
			print(f'Stats sender is: {self.user}')
			if 'stats' not in games[self.game_id]:
				print(f'No Stats found: {self.user}')
				games[self.game_id]['stats'] = '1'
				print(f'{self.user} first quiter')
				# await self.send(text_data=json.dumps({'game_over': ''}))
				other_user = games[self.game_id]['host']
				if other_user == self:
					other_user = games[self.game_id]['opponent']
				# await self.channel_layer.group_send(self.group_name,
				# 		{
				# 			'type' : 'broadcast',
				# 			'game_over' : str(json_text_data['stats']),
				# 			'id': other_user.user.id
						# })
				await other_user.send(text_data=json.dumps(
					{
						'game_over' : json.dumps(json_text_data['stats'])
					}
				))
				await other_user.close(code=4998)
				# games[self.game_id]['stats'] = '1'
				print(f'Samaykom {self.user}:{games[self.game_id]["stats"]}')
				await create_game_record(self, json_text_data['stats'])
				games[self.game_id]['disconnected'].append(self)
				await self.close(code=4999)
			elif 'stats' in games[self.game_id]:
				print(f'States were saved {games[self.game_id]["stats"]}')
				while(await sync_to_async(Game.objects.filter(
        				(Q(player1=games[self.game_id]['host'].user) & Q(player2=games[self.game_id]['opponent'].user))
                               				| (Q(player1=games[self.game_id]['opponent'].user) & Q(player2=games[self.game_id]['host'].user))).first)() == None):
					print('waiting....') 
				print(f'{self.user.first_name} {json_text_data["stats"]}')
				print(f'{self.user} second quiter')
				# games[self.game_id]['stats'] = '2'
				games[self.game_id]['disconnected'].append(self)
				# await self.close()
	
	async def	broadcast(self, event):
		if 'key' in event:
			if not self.user.id == event['id']:
				await self.send(text_data=json.dumps(event))
		# elif 'game_over' in event and self.user.id == event['id']:
		# 	print('Ha game over jat: ', self.user)
		# 	if self.game_id in games and self not in games[self.game_id]['disconnected']:
		# 		await self.send(text_data=json.dumps(
		# 			{
		# 				'game_over' : event['game_over']
		# 			}
		# 		))
				# print('Safi sed: ', self.user)
				# games[self.game_id]['stats'] = '2'
				# await self.close()
		else:
			if self.game_id in games and self not in games[self.game_id]['disconnected']:
				await self.send(text_data=json.dumps(event))

	
	async def	send_aspect(self, event):
		if not self.user.id == event['id']:
			await self.send(json.dumps(
				{
					'aspect': event['aspect']
				}
			))

	async def	disconnect(self, code):
		if code == 4000 or code == 4998:
		#	print('code in game: ', code)
			return

		await self.channel_layer.group_discard(self.group_name, self.channel_name)

		if code == 4999:
			print(f'{self.user}:{self.user.id} sala tarh')
			print(f'Ana f else: {self.user}')
			games.pop(self.game_id)
			await self.channel_layer.group_send("notification",
									{
										'type': 'release_game_id',
										'index': self.game_id,
										'user_id': self.user.id
									})
			return
		
		# await sync_to_async(self.user.update)(user_state='offline')

		print('*********** user in game disconnect(): ', self.user)
		# print('gamessss in disconnect of one of them:::::>>>>>> ', games)
		
		if self.game_id in games:
			# in case one started game and left before opponent join
			if 'opponent' not in games[self.game_id]:
				print(f'{self.user} has no opponent')
				games.pop(self.game_id)
				await self.channel_layer.group_send('notification',
										{
											'type': 'release_game_id',
											'index': self.game_id,
											'user_id': self.user.id,
											'salam': 'cv' # for debugging
										})
			elif 'stats' not in games[self.game_id]: # one left before game ends
				print('host.user: ', games[self.game_id]['host'].user)
				print('opponent.user: ', games[self.game_id]['opponent'].user)
				if self == games[self.game_id]['host']:
					op = games[self.game_id]['opponent']
					print(f'{op.user} ana rani opponent')
				else:
					op = games[self.game_id]['host']
					print(f'{op.user} ana rani host')
				
				print('Ana khrjt  ', op.user)
				await op.send(text_data=json.dumps(
					{
						'game_over': 'salam'
					}
				))
			# else:
			# 	print(f'{self.user}:{self.user.id} sala tarh')
			# 	# if self.game_id in games:
			# 	if games[self.game_id]['stats'] == '2':
			# 		print(f'Ana f else: {self.user}')
			# 		games.pop(self.game_id)
			# 		await self.channel_layer.group_send("notification",
			# 								{
			# 									'type': 'release_game_id',
			# 									'index': self.game_id,
			# 									'user_id': self.user.id
			# 								})
