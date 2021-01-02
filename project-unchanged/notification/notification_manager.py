from .firebase_config import messaging
from users.models import User

class NotificationManager:
	"""
	Class dedicate to manage notifications
	"""
	# TODO: Add notification to database
	def sendToUser(self, user:User, title:str, body:str, data:dict, image:str=None):
		"""
			Send a notification to all a user's devices 
		"""
		tokens = self.__get_tokens_user__(user)
		response = self.__send_notification__(title, body, data, tokens, image)
		return self.__response__(response, len(tokens))
		
	# TODO: Add notifications to database
	def sendToAllUsers(self, title:str, body:str, data:dict, image:str=None):
		"""
			Send a notification to all users
		"""

		tokens, users = self._get_tokens_all_users__()
		response = self.__send_notification__(title, body, data, tokens, image)
		return self.__response__(response, len(tokens))

	def __response__(self, response, devices:int):
		if response != None:
			count = response.success_count
			return {'success': count, "faild": devices-count}
		return {'success': 0, "faild": devices}

	def __send_notification__(self, title:str, body:str, data:dict, registation_tokens:list, image:str=None):
		"""
			Send a notification
		"""
		notification = messaging.Notification(title=title, body=body)
		if registation_tokens != None:
				count_tokens = len(registation_tokens)
				if count_tokens > 0:
					message = messaging.MulticastMessage(
						data=data, notification=notification, tokens=registation_tokens,
						android=messaging.AndroidConfig(
							notification=messaging.AndroidNotification(title=title, body=body, image=image)
						)
					)
					return messaging.send_multicast(message)
		return None

	def __get_tokens_user__(self, user:User):
		devices = user.devices
		tokens = []
		if devices != None:
			for device in devices:
				token = device['token']
				if token != None:
					tokens.append(token)
		return tokens
	
	def _get_tokens_all_users__(self):
		devices = []
		users = User.objects.exclude(devices=None)
		for user in users:
			devices += self.__get_tokens_user__(user)
		return devices, users

class NotificationType:
	"""
		Types of notifications avalibles in the system
	"""
	CHANGE_PRIVACY_POLICES = 'change_privacy_polices'
	PURCHASE_DONE = 'purchase_done'
	TIP = 'tip'
	ADVERTISEMENT = 'advertisement'
	DISABLE_USER = 'disable_user'
	ENABLE_USER = 'enable_user'
	TRANSFER ='trasfer'
		