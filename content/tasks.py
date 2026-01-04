import subprocess
import os

def convert_480p(source):
    base, ext = os.path.splitext(source)
    new_file = base + '_480p.mp4'

    os.makedirs(os.path.dirname(new_file), exist_ok=True)

    # cmd = 'ffmpeg -i "{}" -s hd480 -c:v libx264 -crf 23 -c:a aac -strict -2 "{}"'.format(source, new_file)
    cmd = [
        "ffmpeg",
        "-y",
        "-i", source,
        "-s", "hd480",
        "-c:v", "libx264",
        "-crf", "23",
        "-c:a", "aac",
        "-strict", "-2",
        new_file
    ]
    # subprocess.run(cmd, check=True)

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("FFMPEG STDOUT:", result.stdout)
    print("FFMPEG STDERR:", result.stderr)