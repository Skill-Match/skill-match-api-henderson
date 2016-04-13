from django.test import TestCase

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import Profile


class UserTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='joe',
                                             email='test@test.com',
                                             password='password')
        Profile.objects.create(user=self.user, gender='Male', age="30's",
                               wants_texts=True)

    def test_created_token(self):
        self.assertEqual(hasattr(self.user, 'auth_token'), True)

    def test_obtain_auth_token(self):
        data = {"username": self.user.username, "password": 'password'}
        url = reverse('obtain_auth_token')
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['user_id'], self.user.id)

    def test_create_user_profile_token(self):
        url = reverse('register_user')
        data = {'username': 'bob', 'email': 'email@email.com', 'password':
                'pwd', 'profile': {'gender': "Male", 'age': "20's",}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['username'], 'bob')
        self.assertEqual(response.data['profile']['gender'], 'Male')
        bob = User.objects.get(username='bob')
        self.assertEqual(hasattr(bob, 'auth_token'), True)

    def test_detail_update_user(self):
        url = reverse('user-detail', kwargs={'pk': self.user.id})
        response = self.client.get(url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        response = self.client.put(url, {'username': 'bob',
                                         'email': 'email@email.com',
                                         'password': 'pwd',
                                         'profile': {'gender': "Male",
                                                     'age': "20's",
                                                     "phone_number": "508-252-2525",
                                                     'wants_texts': True}},
                                   format='json')
        self.assertEqual(response.data['username'], 'bob')
        self.assertEqual(response.data['profile']['age'], "20's")