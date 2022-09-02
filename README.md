# audio-to-video

A Python project to convert a .mp3 audio file into a .mp4 video file and upload this file into Youtube.

## To convert .mp3 into .mp4 using an image

Clone the repo and move into the main repo directory.

Create a env, activate and install ffmpeg:

```text
pip install ffmpeg-python gooey
```

Run the Gooey app:

```text
python run.py
```

 > Make sure there are not spaces in the file path's of the .mp3 or image or their parent directories

If this doesn't work, the raw ffmpeg command is below:

```text
ffmpeg -loop 1 -i image.png -i audio.mp3 -c:a copy -c:v libx264 -shortest video.mp4
```

When issues on Windows it might be needed to copy ffmpeg.exe into Python folder