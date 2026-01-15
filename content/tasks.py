import os
import subprocess
from django.conf import settings


def convert_to_hls(input_file: str, video_id: int) -> None:
    
    profiles = [
        {'resolution':'480p','scale': '850x480', 'bitrate': '1000k'},
        {'resolution':'720p','scale': '1280x720', 'bitrate': '2500k'},
        {'resolution':'1080p','scale': '1920x1080', 'bitrate': '5000k'},
    ]
    video_root = os.path.join(settings.MEDIA_ROOT, 'videos', str(video_id))

    for profile in profiles:
        resolution_dir = os.path.join(video_root, profile['resolution'])
        os.makedirs(resolution_dir, exist_ok=True)
        playlist_file = os.path.join(resolution_dir, f"index.m3u8")

        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f"scale={profile['scale']}",
            '-c:v', 'libx264',
            '-b:v', profile['bitrate'],
            '-c:a', 'aac',
            '-b:a', '128k',
            '-start_number', '0',
            '-hls_time', '5',
            '-hls_list_size', '0',         
            '-f', 'hls',
            playlist_file,
        ]

        subprocess.run(cmd, check=True)


def delete_origin_video_file(source):

    if os.path.isfile(source):
        os.remove(source)