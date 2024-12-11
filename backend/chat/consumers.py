from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from .models import *
from notification.models import Notification
from .serializers import *
from django.db.models import Q
from friend.models import Friendship

participants = {}

class	ChatConsumer(AsyncWebsocketConsumer):
	async def	extract_friend_id(self):
		split = self.conversation_name.split('_')
		id1 = int(split[0])
		id2 = int(split[1])
		if self.user.id not in [id1, id2]:
			await self.send(text_data=json.dumps({'error': 'You are not part of this conversation'}))
			await self.close(code=4000)
			print('closiiiit')
			return

		if self.user.id != id2:
			return id2
		return id1


	async def	connect(self):
		print('participants before: ', participants)
		await self.accept()

		self.user = self.scope['user']
		self.conversation_name = self.scope['url_route']['kwargs']['conversation_name']
		friend_id = await self.extract_friend_id() # checks and close
		
		try:
			self.friendship = await sync_to_async(Friendship.objects.get)(
					Q(user1=self.user.id, user2=friend_id) | Q(user1=friend_id, user2=self.user.id)
					& Q(status='accepted'))

		except Friendship.DoesNotExist:
			print('id ', self.user.id)
			print('first_name ', self.user.first_name)
			s = f'{self.conversation_name}:No friendship with {friend_id}'
			await self.send(json.dumps({'error': s}))
			await self.close(code=4000)
			return

		self.friend = await sync_to_async(UserAccount.objects.get)(id=friend_id)

		self.conversation = await sync_to_async(Conversation.objects.filter)(Q(user1=self.user, user2=self.friend)
																	   | Q(user1=self.friend, user2=self.user))
	
		self.conversation = await sync_to_async(self.conversation.first)()
	
		if self.conversation == None:
			self.conversation = await sync_to_async(Conversation.objects.create)(user1=self.user, user2=self.friend)

		await self.channel_layer.group_add(self.conversation_name, self.channel_name)

		if not self.conversation_name in participants:
			participants[self.conversation_name] = 0

		participants[self.conversation_name] += 1
		print('participants after: ', participants)

		# messages = await sync_to_async(Message.objects.filter)(conversation=self.conversation_name)
		# await self.send(text_data=json.dumps(
		# 	{
		# 		'messages': MessageSerializer(messages, many=True).data
		# 	}
		# ))

	
	async def	disconnect(self, code):
		print('code: ', code)
		if code != 4000:
			await self.channel_layer.group_discard(self.conversation_name, self.channel_name)
			participants[self.conversation_name] -= 1
			if participants[self.conversation_name] == 0:
				participants.pop(self.conversation_name)

		print('participants after disconnect(): ', participants)

	
	async def	receive(self, text_data=None, bytes_data=None):
		try:
			json_text_data = json.loads(text_data)
			if self.friendship.status == 'accepted':
				if 'message' in json_text_data:
					await self.channel_layer.group_send(self.conversation_name,
														{
															'type': 'broadcast_message',
															'message': json_text_data['message'],
															'sender': self.user 
														})
					Message.objects.create(content=json_text_data['message'],
												conversation=self.conversation,
													owner=self.user)
				elif 'block' in json_text_data:
					self.friendship.status = 'bloked'
					self.friendship.last_action_by = self.user.id
					self.friendship.save() # maybe need sync_to_asyn
					# await self.group_send('notification',
					# 		  {
					# 			'type': 'take_action',
					# 			'notification_type': 'block', 
					# 			'description': '',
					# 			'receiver': '',
					# 			'sender': '',
					# 			'timestamp': ''
					# 		  })
			else:
				if 'unblock' in json_text_data and self.friendship.last_action_by == self.user.id:
					self.friendship.status = 'accepted'
					self.friendship.last_action_by = self.user.id
					self.friendship.save()
			
		except json.JSONDecodeError:
			await self.send(text_data=json.dumps({'error': 'Invalid json format'}))


	async def	broadcast_message(self, event):
		if self.user.id == event['sender']:
			if participants.__len__() < 2:
				description = f"{event['sender']} sends you a message!"
				notificiation = Notification.objects.create(
					description=description,
					sender=self.user,
					receiver=self.friend,
					type='chat'
				)
				await self.channel_layer.group_send('notification',
										{
											'type': 'send_notification',
											'notification_type': 'chat',
											'description': description,
											'sender': self.user,
											'receiver': self.friend,
											'timestamp': notificiation.timestamp
										})

		if self.user.id != event['sender'].id:
			await self.send(text_data=json.dumps(
				{
					'message': event['message']
				}
			))
