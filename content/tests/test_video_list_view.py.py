from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from content.models import Video


User = get_user_model()

class VideoListViewTest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="secret"
        )

        self.video = Video.objects.create(
            title="Test Video"
        )

        self.client.force_authenticate(user=self.user)

    def test_get_video_list_authenticated(self):
        url = reverse("video-list")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.video.id)

    def test_get_video_list_unauthenticated(self):
        self.client.force_authenticate(user=None)

        url = reverse("video-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)