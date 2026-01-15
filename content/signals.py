import os
import django_rq
import shutil
from django.dispatch import receiver
from django.conf import settings
from django.db.models.signals import post_save, post_delete
from content.models import Video
from content.tasks import (
    convert_to_hls, 
    delete_origin_video_file
)


@receiver (post_save, sender=Video)
def video_post_save(sender, instance, created, **kwargs):
    if created and instance.video_file:
        source = instance.video_file.path
        if os.path.exists(source):
            queue  = django_rq.get_queue('default', autocommit=True)
            convert_video = queue.enqueue(convert_to_hls, source, instance.id)
            queue.enqueue(
                delete_origin_video_file, source,
                depends_on=convert_video
            )


@receiver(post_delete, sender=Video)       
def auto_delete_files_on_video_delete(sender, instance, **kwargs):
   
    if instance.video_file and os.path.isfile(instance.video_file.path):
        os.remove(instance.video_file.path)

    hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(instance.id))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)

    if instance.thumbnail and os.path.isfile(instance.thumbnail.path):
        os.remove(instance.thumbnail.path)