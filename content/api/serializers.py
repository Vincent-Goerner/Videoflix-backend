from rest_framework import serializers

from content.models import Video


class VideoListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title', 'description', 'thumbnail', 'category']

    def get_thumbnail(self, obj):
        thumbnail = getattr(obj, "thumbnail", None)

        if not thumbnail or not thumbnail.name:
            return None

        request = self.context.get("request")
        url = thumbnail.url

        return request.build_absolute_uri(url) if request else url