from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status

class RegistrationTest(APITestCase):
    
    def setUp(self):
        self.url = reverse('register')
        self.valid_user = {
            'password': 'valid_password',
            'email': 'valid@email.com',
            'confirmed_password': 'valid_password'
        }
        self.invalid_user = {
            'password': 'invalid_password',
            'email': 'invalid@email.com',
            'confirmed_password': 'invalid-password'
        }
        self.existing_user = User.objects.create_user(
            email="existing@example.com",
            password="password123"
        )

    def test_post_valid_registration(self):
        response = self.client.post(self.url, self.valid_user, format="json")

        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

    def test_post_inavlid_registration(self):
        response = self.client.post(self.url, self.invalid_user, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords do not match", response.data["confirmed_password"][0])
    
    def test_post_existing_user_registration(self):
        payload = {
            "password": "password123",
            "confirmed_password": "password123",
            "email": "unique_email@example.com",
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)
        self.assertIn("A user with that email already exists.", response.data["email"][0])

    def test_post_existing_email_registration(self):
        payload = {
            "password": "password123",
            "confirmed_password": "password123",
            "email": "existing@example.com",
        }
        response = self.client.post(self.url, payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)