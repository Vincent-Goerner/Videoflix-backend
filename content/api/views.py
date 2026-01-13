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