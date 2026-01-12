import subprocess
import os

def convert_to_resolution(source):

    resolutions = ['480', '720', '1080']

    for resolution in resolutions:
        base, ext = os.path.splitext(source)
        new_file = base + f'_{resolution}p.mp4'

        os.makedirs(os.path.dirname(new_file), exist_ok=True)

        cmd = [
            'ffmpeg',
            '-y',
            '-i', source,
            '-s', f'hd{resolution}',
            '-c:v', 'libx264',
            '-crf', '23',
            '-c:a', 'aac',
            '-strict', '-2',
            new_file
        ]

        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        print('FFMPEG STDOUT:', result.stdout)
        print('FFMPEG STDERR:', result.stderr)