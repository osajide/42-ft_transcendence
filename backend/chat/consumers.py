from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json
from .models import *
from notification.models import Notification
from .serializers import *
from django.db.models import Q
from friend.models import Friendship

participants = {}
frienships = {}

def	load_messages(self):
	seen = self.conversation.messages.filter(Q(seen_by_receiver=True) | (Q(seen_by_receiver=False) & (Q(owner=self.user))))
	unseen = self.conversation.messages.filter(Q(owner=self.friend) & Q(seen_by_receiver=False))
	ser1 = MessageSerializer(seen, many=True)
	ser2 = MessageSerializer(unseen, many=True)
	# print('ser22222::::: ', ser2.data)
	return [ser1.data, ser2.data]

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
					& (Q(status='accepted') | (Q(status='blocked')))).first)()

			if self.friendship is not None:
				self.conversation =  await sync_to_async(Conversation.objects.filter(Q(user1=self.user, user2=self.friend)
																	   | Q(user1=self.friend, user2=self.user)).first)()
				if self.conversation is None:
					self.conversation = await sync_to_async(Conversation.objects.create)(user1=self.user, user2=self.friend)
				else:
					msgs = await sync_to_async(load_messages)(self)
					await self.send(text_data=json.dumps(
						{
							'history': msgs,
							'status': self.friendship.status,
							'last_action_by': self.friendship.last_action_by
						}
					))
					temp = await sync_to_async(self.conversation.messages.filter)(Q(owner=self.friend) & Q(seen_by_receiver=False))
					await sync_to_async(temp.update)(seen_by_receiver=True)


				await self.channel_layer.group_add(self.conversation_name, self.channel_name)

				if not self.conversation_name in participants:
					participants[self.conversation_name] = 0
					frienships[self.conversation_name] = self.friendship

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
			frienships.pop(self.conversation_name)

		print('participants after disconnect(): ', participants)

	
	async def	receive(self, text_data=None, bytes_data=None):
		print('paritcipants in receive: ', participants)
		try:
			json_text_data = json.loads(text_data)
			if frienships[self.conversation_name].status == 'accepted':
				if 'block' in json_text_data:
					frienships[self.conversation_name].status = 'blocked'
					frienships[self.conversation_name].last_action_by = self.user.id
					await sync_to_async(frienships[self.conversation_name].save)()
				elif 'message' in json_text_data:
					await self.channel_layer.group_send(self.conversation_name,
														{
															'type': 'broadcast_message',
															'message': json_text_data['message'],
															'sender_id': self.user.id
														})
				# elif 'challenge' in json_text_data:
				# 	print('challenge req ********')
				# 	if self.user.user_state == 'in_game':
				# 		await self.send(text_data=json.dumps({'error': 'already in game'}))
				# 		return
				# 	print('challenge notification sent !!!!!!!!')
				# 	await self.channel_layer.group_send('notification',
				# 							{
				# 								'type': 'make_match',
				# 								'id': self.user.id,
				# 								'opponent': self.friend.id,
				# 								'challenge' : True
				# 							})

			elif frienships[self.conversation_name].status == 'blocked':
				if 'unblock' in json_text_data and frienships[self.conversation_name].last_action_by == self.user.id:
					frienships[self.conversation_name].status = 'accepted'
					frienships[self.conversation_name].last_action_by = self.user.id
					await sync_to_async(frienships[self.conversation_name].save)()
				elif frienships[self.conversation_name].last_action_by == self.user.id:
					await self.send(text_data=json.dumps({"reject": f"you have blocked {self.friend}"}))
				else:
					await self.send(text_data=json.dumps({"reject": f"you've been blocked by {self.friend}"}))

		except json.JSONDecodeError:
			await self.send(text_data=json.dumps({'error': 'Invalid json format'}))


	async def	broadcast_message(self, event):
		seen = True

		if self.user.id == event['sender_id']:
			if participants[self.conversation_name] < 2:
				seen = False
				description = f"{self.user} sends you a message!"
				print('desc: ', description)
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
											'receiver': UserSerializer(self.friend).data,
											'timestamp': str(notificiation.timestamp),
											'id': notificiation.id
										})

			await sync_to_async(Message.objects.create)(content=event['message'],
												conversation=self.conversation,
													owner=self.user,
														seen_by_receiver=seen)

		if self.user.id != event['sender_id']:
			if 'message' in event:
				await self.send(text_data=json.dumps(
					{
						'message': event['message']
					}
				))
	

