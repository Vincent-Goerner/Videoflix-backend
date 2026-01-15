import os
from django.http import FileResponse, HttpResponse, Http404
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from content.models import Video
from content.api.serializers import VideoListSerializer
from content.api.permissions import CookieJWTAuthentication


class VideoListView(APIView):

    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get(self, request):
        videos = Video.objects.all()
        serializer = VideoListSerializer(
            videos,
            many=True,
            context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseHLSVideoView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [CookieJWTAuthentication]

    def get_video_or_404(self, movie_id: int) -> Video:
        try:
            return Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video not found")

    def build_video_path(self, movie_id: int, resolution: str, filename: str) -> str:
        path = os.path.join(
            settings.MEDIA_ROOT,
            "video",
            str(movie_id),
            resolution,
            filename,
        )
        if not os.path.exists(path):
            raise Http404("File not found")
        return path
    

class VideoPlaylistView(BaseHLSVideoView):

    def get(self, request, movie_id: int, resolution: str) -> HttpResponse:
        self.get_video_or_404(movie_id)

        manifest_path = self.build_video_path(
            movie_id=movie_id,
            resolution=resolution,
            filename="index.m3u8",
        )

        try:
            with open(manifest_path, "r", encoding="utf-8") as file:
                return HttpResponse(
                    file.read(),
                    content_type="application/vnd.apple.mpegurl",
                    status=status.HTTP_200_OK,
                )
        except OSError:
            raise Http404("Error reading manifest file")
        

class HLSVideoSegmentView(BaseHLSVideoView):

    def get(self, request, movie_id: int, resolution: str, segment: str) -> FileResponse:
        self.get_video_or_404(movie_id)

        segment_path = self.build_video_path(
            movie_id=movie_id,
            resolution=resolution,
            filename=segment,
        )

        try:
            return FileResponse(
                open(segment_path, "rb"),
                content_type="video/MP2T",
                status=status.HTTP_200_OK,
            )
        except OSError:
            raise Http404("Error reading segment file")