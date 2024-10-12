from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create your tests here.
class UserAuthTests(APITestCase):
    def test_user_registration(self):
        url = reverse('register')  # Assuming your URL name for registration is 'register'
        data = {
            'username': 'testuser',
            'password': 'testpassword123',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)  # Token should be in the response
    def test_user_login(self):
        # Create a user first
        user = User.objects.create_user(username='testuser', password='testpassword123')
        url = reverse('login')  # Assuming your URL name for login is 'login'
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)  # Token should be in the response
    def test_user_logout(self):
        # Create a user and login
        user = User.objects.create_user(username='testuser', password='testpassword123')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        url = reverse('logout')  # Assuming your URL name for logout is 'logout'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Successful logout")
