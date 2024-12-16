from chat.models import *
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import Notification
from .serializers import NotificationSerializer
from authentication.serializers import UserSerializer
from channels.db import database_sync_to_async

import redis

redis_client = redis.Redis(host='redis', port=6379, db=1)

games = []
tournaments = []
user_index = {}

@database_sync_to_async
def get_notifications(id):
	notifications = Notification.objects.filter(receiver=id)
	serializer = NotificationSerializer(notifications, many=True)
	json_str = json.dumps(serializer.data)
	return json_str

@database_sync_to_async
def	delete_notification(id):
	notification = Notification.objects.filter(id=id).first()
	if notification is not None:
		notification.delete()

class	NotificationConsumer(AsyncWebsocketConsumer):

	notification_group = 'notification'
	async def	connect(self):
		print('ja')
		await self.accept()

		if self.scope['user'].is_authenticated is False:
			await self.send(json.dumps(
					{
						'error': 'Invalid Token'
					}
				))
			# await self.close()
			return

		print('which user: ', self.scope['user'])
		await self.channel_layer.group_add(self.notification_group, self.channel_name)
		notifications = await get_notifications(self.scope['user'].id)
		await self.send(text_data=notifications)

	async def	disconnect(self, code):
		await self.channel_layer.group_discard(self.notification_group, self.channel_name)
		print("=====> DISCONNECTED IN NOTIFICATION")
		if (len(tournaments) > 0) and (self.scope['user'].id in user_index
					) and (tournaments[user_index[self.scope['user'].id]] != '0' 
					) and tournaments[user_index[self.scope['user'].id]] != '8':
			tournaments[user_index[self.scope['user'].id]] = chr(ord(tournaments[user_index[self.scope['user'].id]]) - 1)
			print(f"tounaments {user_index[self.scope['user'].id]} still has {tournaments[user_index[self.scope['user'].id]]} players")

		# print('games noti: ', games)
		# games.clear() #temp
		# await self.close()

	async def	receive(self, text_data=None, bytes_data=None):
		
		json_text_data = json.loads(text_data)
		if 'seen' in json_text_data:
			await delete_notification(json_text_data['seen'])
		elif 'private' in json_text_data:
			print('jsno pri: ', json_text_data)
			await self.channel_layer.group_send(self.notification_group,
									   {
										   'type': 'make_match',
										   'id': self.scope['user'].id,
										   'opponent': json_text_data['private'],
										   'private' : True
									   })
	
		elif 'solo' in json_text_data:
			print('receive solo id: ', self.scope['user'].id, ': ', self.scope['user'].first_name)
			await self.channel_layer.group_send(self.notification_group,
									   {
										   'type': 'make_match',
										   'id': self.scope['user'].id
									   })

		elif 'tournament'  in json_text_data:

			if self.scope['user'].user_state != "offline":
				await self.send(json.dumps(
					{
						'error': 'The actual tournament not disponible for this user'
					}
				))
				return 


			ascii_value = 55
			while (True): 
				try:
					index = tournaments.index(chr(ascii_value))
					# tournaments[index] =  chr(ord(tournaments[index]) + 1)
					break
				except ValueError:
					ascii_value -= 1
					if ascii_value < 48:
						tournaments.append('0')
						redis_client.set(f"tournament_len", len(tournaments))
						index = len(tournaments) - 1
						break
			if self.scope['user'].id not in user_index:
				user_index[self.scope['user'].id] = []
			user_index[self.scope['user'].id] = index
			print("notf array: ", user_index)
			print(f"tournament : {index} => {tournaments[index]}")
			await self.send(json.dumps(
				{
					'tournament_id': index
				}
			))

	async def 	update_tournament(self, event):
		
		if (event['user_id'] == self.scope['user'].id): 
			print("UPDATE TOURNAMENT")
			tournaments[event['id']] = chr(ord(tournaments[event['id']]) + event['value'])
			if (event['user_id'] in user_index) and (event['state'] == 'disconnect'):
				print("POPPED FROM NOTIFICATION") 
				user_index.pop(event['user_id']) 
			print(f"tournament {event['id']} has {tournaments[event['id']]} elements")

	async def 	generate_games(self, event):
		if event['user_id'] != self.scope['user'].id:
			return 
		indexes = []
		print("generating games")
		i = 0
		while (i < event['nb_of_games']):
			try:
				index = games.index('0')
				games[index] = '2'
			except ValueError:
				games.append('2')
				index = len(games) - 1

			indexes.append(index)
			i += 1

		await self.channel_layer.group_send(event['tournament_group'],
            {
                'type' : 'match_making',   
                'games' : indexes,
                'last_user' : event['last_user']
            })

	async def	send_notification(self, event):
		if 'receiver' in event:
			if self.scope['user'].id == event['receiver']['id']:
				await self.send(text_data=json.dumps([
					{
						'type': event['notification_type'],
						'description': event['description'],
						'sender': event['sender'],
						'timestamp': event['timestamp'],
						'id': event['id']
				}]))
		elif 'opponent' in event:
			if self.scope['user'].id == event['opponent']:
				print('ana opponent')
				await self.send(text_data=json.dumps({
					'game_invite': {
						# 'type': 'game',
						'description': f"{event['sender']['first_name'].capitalize()} {event['sender']['last_name'].upper()} invited you to a game",
						'sender': event['sender'],
						# 'timestamp': event['timestamp'],
						'game_id': event['game_id']
				}}))


	async def	make_match(self, event):
		# print('games list before: ', games)
		if self.scope['user'].id == event['id']:
			if 'private' in event:
				try:
					index = games.index('0')
					games[index] = '2'
				except ValueError:
					games.append('2')
					index = len(games) - 1

				print('notification sent')
				await self.channel_layer.group_send('notification',
						  {
							  'type': 'send_notification',
							  'game_id': index,
							  'sender' : UserSerializer(self.scope['user']).data,
							  'opponent': int(event['opponent'])
						  })
			else:
				try:
					index = games.index('1')
					games[index] = '2'
				except ValueError:
					try:
						index = games.index('0')
						games[index] = '1'
					except ValueError:
						games.append('1')
						index = len(games) - 1

			await self.send(json.dumps(
				{
					'game_id': index
				}
			))

			redis_client.set('max_games', len(games))

			if not index in users_and_games:
				users_and_games[index] = []
			users_and_games[index].append(self.scope['user'].id)

	async def	release_game_id(self, event):
		games[event['id']] = '0'
		