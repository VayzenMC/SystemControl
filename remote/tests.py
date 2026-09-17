import json

from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Command, Device


class RemoteApiTests(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(
			username='operator',
			password='strong-test-password',
		)

	def test_anonymous_user_cannot_access_dashboard_or_api(self):
		dashboard = self.client.get('/')
		devices = self.client.get('/api/devices/')

		self.assertRedirects(dashboard, '/login/?next=/')
		self.assertEqual(devices.status_code, 401)

	def test_user_can_login_and_access_dashboard(self):
		login_response = self.client.post(
			'/login/',
			{'username': 'operator', 'password': 'strong-test-password'},
		)

		self.assertRedirects(login_response, '/')
		self.assertEqual(self.client.get('/api/devices/').status_code, 200)

	def test_agent_can_register_and_poll(self):
		response = self.client.post(
			'/api/register/',
			data=json.dumps({'name': 'Test PC'}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		token = response.json()['token']
		self.assertTrue(Device.objects.filter(device_token=token).exists())

		poll = self.client.get(f'/api/client/{token}/poll/')
		self.assertEqual(poll.status_code, 200)
		self.assertFalse(poll.json()['has_command'])

	def test_command_response_uses_agent_output_key(self):
		device = Device.objects.create(name='Test PC')
		command = Command.objects.create(device=device, command_text='whoami')

		response = self.client.post(
			f'/api/client/{device.device_token}/response/',
			data=json.dumps({'command_id': command.id, 'output': 'user'}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		command.refresh_from_db()
		self.assertEqual(command.response_text, 'user')
		self.assertTrue(command.is_executed)
