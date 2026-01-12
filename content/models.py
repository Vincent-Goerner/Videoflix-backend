from django.db import models
from datetime import date

MOVIE_CATEGORY = [
    ('action', 'Action'),
    ('adventure', 'Adventure'),
    ('comedy', 'Comedy'),
    ('drama', 'Drama'),
    ('documentation', 'Documentation'),
    ('horror', 'Horror'),
    ('sci-fi', 'Sci-fi'),
    ('thriller', 'Thriller'),
    ('western', 'Western'),
    ('fantasy', 'Fantasy'),
    ('crime', 'Crime'),
    ('romance', 'Romance')
]

class Video(models.Model):
    created_at = models.DateField(default=date.today)
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='video', blank=True, null=True)
    thumbnail_url = models.ImageField(upload_to="thumbnail/", blank=True, null=True)
    category = models.CharField(max_length=30, choices=MOVIE_CATEGORY, default='')

    def __str__(self):
        return self.title
