import os
import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from content.models import Video


User = get_user_model()

class VideoPlaylistViewTest(APITestCase):

    def setUp(self):
        self._temp_media = tempfile.mkdtemp()
        self._old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self._temp_media

        self.user = User.objects.create_user(
            username="testuser",
            password="secret"
        )

        self.video = Video.objects.create(
            title="Test Video"
        )

        self.client.force_authenticate(user=self.user)

    def tearDown(self):
        settings.MEDIA_ROOT = self._old_media_root
        shutil.rmtree(self._temp_media)

    def _create_manifest(self, resolution="720p"):
        base_path = os.path.join(
            settings.MEDIA_ROOT,
            "video",
            str(self.video.id),
            resolution,
        )
        os.makedirs(base_path, exist_ok=True)

        manifest_path = os.path.join(base_path, "index.m3u8")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write("#EXTM3U")

    def test_get_playlist_success(self):
        self._create_manifest()

        url = reverse(
            "video-playlist",
            kwargs={
                "movie_id": self.video.id,
                "resolution": "720p",
            },
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.apple.mpegurl"
        )
        self.assertIn("#EXTM3U", response.content.decode())

    def test_get_playlist_video_not_found(self):
        url = reverse(
            "video-playlist",
            kwargs={
                "movie_id": 9999,
                "resolution": "720p",
            },
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_playlist_file_not_found(self):
        url = reverse(
            "video-playlist",
            kwargs={
                "movie_id": self.video.id,
                "resolution": "720p",
            },
        )

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)