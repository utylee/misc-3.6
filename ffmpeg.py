import subprocess

#subprocess.run('/mnt/e/Down/ffmpeg-3.2.4/bin/ffmpeg.exe -i \
#                /mnt/c/Users/utylee/11.mp4 -c:a copy -c:v copy -g 1 -ss 00:06:18 -to 00:10:39 out.mp4', shell=True)

subprocess.run('/mnt/e/Down/ffmpeg-3.2.4/bin/ffmpeg.exe -i \
        c:/Users/utylee/11.mp4 -c:a copy -c:v copy -g 1 \
        -ss 00:52:56 \
        -to 00:55:54 out.mp4', shell=True)
