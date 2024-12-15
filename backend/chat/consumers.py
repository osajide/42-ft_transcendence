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

	async def	connect(self):
		print('participants before: ', participants)
		await self.accept()

		self.user = self.scope['user']
		if self.user.is_authenticated == False:
			await self.send(text_data=json.dumps({'error': 'user not authenticated'}))
			await self.close(code=4000)
			return

		self.conversation_name = [self.scope['url_route']['kwargs']['id'], self.user.id]
		self.conversation_name.sort()
		self.conversation_name = f'{self.conversation_name[0]}_{self.conversation_name[1]}'

		self.friend = await sync_to_async(UserAccount.objects.filter(id=self.scope['url_route']['kwargs']['id']).first)()

		if self.friend is not None:
			self.friendship = await sync_to_async(Friendship.objects.filter(
					Q(user1=self.user, user2=self.friend) | Q(user1=self.friend, user2=self.user.id)
					& Q(status='accepted')).first)()

			if self.friendship is not None:
				self.conversation =  await sync_to_async(Conversation.objects.filter(Q(user1=self.user, user2=self.friend)
																	   | Q(user1=self.friend, user2=self.user)).first)()
				if self.conversation is None:
					self.conversation = await sync_to_async(Conversation.objects.create)(user1=self.user, user2=self.friend)

				await self.channel_layer.group_add(self.conversation_name, self.channel_name)

				if not self.conversation_name in participants:
					participants[self.conversation_name] = 0

				participants[self.conversation_name] += 1
				print('participants after: ', participants)
				return

		await self.send(text_data=json.dumps({'error': 'conversation not found'}))
		await self.close(code=4000)

	
	async def	disconnect(self, code):
		print('code: ', code)
		if code == 4000:
			return

		await self.channel_layer.group_discard(self.conversation_name, self.channel_name)
		participants[self.conversation_name] -= 1
		if participants[self.conversation_name] == 0:
			participants.pop(self.conversation_name)

		print('participants after disconnect(): ', participants)

	
	async def	receive(self, text_data=None, bytes_data=None):
		print('paritcipants in receive: ', participants)
		try:
			json_text_data = json.loads(text_data)
			if self.friendship.status == 'accepted':
				if 'message' in json_text_data:
					await self.channel_layer.group_send(self.conversation_name,
														{
															'type': 'broadcast_message',
															'message': json_text_data['message'],
															'sender': self.user.id
														})

					await sync_to_async(Message.objects.create)(content=json_text_data['message'],
												conversation=self.conversation,
													owner=self.user)
			# else:
			# 	if 'unblock' in json_text_data and self.friendship.last_action_by == self.user.id:
			# 		self.friendship.status = 'accepted'
			# 		self.friendship.last_action_by = self.user.id
			# 		self.friendship.save()
			
		except json.JSONDecodeError:
			await self.send(text_data=json.dumps({'error': 'Invalid json format'}))


	async def	broadcast_message(self, event):
		print('event: ', event)
		if self.user.id == event['sender']:
			if participants.__len__() < 2:
				description = f"{event['sender']} sends you a message!"
				notificiation = await sync_to_async(Notification.objects.create)(
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
											'sender': UserSerializer(self.user).data,
											'receiver': UserSerializer(self.friend,).data,
											'timestamp': str(notificiation.timestamp)
										})

		if self.user.id != event['sender']:
			await self.send(text_data=json.dumps(
				{
					'message': event['message']
				}
			))
