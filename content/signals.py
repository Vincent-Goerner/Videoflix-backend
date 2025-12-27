import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
from .models import Video
from .tasks import convert_480p

@receiver (post_save, sender=Video) # Variante 2 zur Verbindung
def video_post_save(sender, instance, created, **kwargs):
    print('Video wurde gespeichert')
    if created:
        print('New Video created')
        convert_480p(instance.video_file.path)

# post_save.connect(video_post_save, sender=Video) # Variante 1 zur Verbindung 

@receiver(post_delete, sender=Video)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)