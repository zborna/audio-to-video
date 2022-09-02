"""
run.py

This script produces a GUI window that converts a .mp3 audio file and an image
into a .mp4 video

@author: peter.kazarinoff
"""

from pathlib import Path
import subprocess
import platform

from simple_youtube_api.Channel import Channel
from simple_youtube_api.LocalVideo import LocalVideo

from gooey import Gooey, GooeyParser


@Gooey(dump_build_config=True, program_name="Audio to Video Conversion Tool")
def main():
    desc = "A Python GUI App to convert a .mp3 and an image into a .mp4"
    mp3_select_help_msg = "Select a .mp3 audio file to process"
    image_select_help_msg = "Select an image file (.png or .jpg) to use in the video"

    my_parser = GooeyParser(description=desc)
    my_parser.add_argument(
        "mp3_to_convert", help=mp3_select_help_msg, widget="FileChooser"
    )
    my_parser.add_argument(
        "image_to_convert", help=image_select_help_msg, widget="FileChooser"
    )
    my_parser.add_argument(
        "output_dir", help="Directory to save output", widget="DirChooser"
    )

    my_parser.add_argument(
        "youtube_title", help="Title"
    )

    my_parser.add_argument(
        "youtube_description", help="Description"
    )
    

    args = my_parser.parse_args()

    # construct the .mp3 input audio file path
    mp3_to_convert_Path = Path(args.mp3_to_convert)

    # construct image file path
    image_to_convert_Path = Path(args.image_to_convert)

    # construct output .mp4 file path
    mp4_outfile_name = str(mp3_to_convert_Path.stem) + ".mp4"
    mp4_outfile_Path = Path(args.output_dir, mp4_outfile_name)
    mp4_outfile_Path.unlink(missing_ok=True) # delete the .mp4 file if it's there

    # Determine ffmpeg executable file path
    """
    where ffmpeg
    """
    if platform.system() == 'Windows':
        ffmpeg_path_bytes = subprocess.check_output("where ffmpeg", shell=True)  # returns bytes
    elif platform.system() == 'Linux':
        ffmpeg_path_bytes = subprocess.check_output("which ffmpeg", shell=True) 

    ffmpeg_executable_path = ffmpeg_path_bytes.decode().strip()
    print("ffmpeg_executable_path: ", ffmpeg_executable_path)

    # create the ffmpeg command
    """
    ffmpeg -loop 1 -i image.png -i audio.mp3 -c:a copy -c:v libx264 -shortest video.mp4
    """
    #original
    #ffmpeg_command = f"-loop 1 -i {image_to_convert_Path} -i {mp3_to_convert_Path} -c:a copy -c:v libx264 -shortest {mp4_outfile_Path}"
    

    # from https://stackoverflow.com/questions/64375367/python-convert-mp3-to-mp4-with-static-image

# -loop 1 makes input.png loop indefinitely.
# -framerate 1 sets input.png input frame rate to 1 fps.
# -map 0 -map 1:a chooses the video from image.png and only the audio from audio.mp3. This is needed in case image.png is smaller than any album/cover art attached to the MP3. Otherwise it may choose the album/cover art instead. See FFmpeg Wiki: Map for more info.
# -r 10 sets output frame rate to 10 fps. Setting input to 1 fps and output to 10 fps is for two reasons:
# It is faster to input as 1 fps and duplicate frames to 10 fps compared to initially setting the input as 10 fps. It makes encoding faster.
# Most players can't play anything under ~6 fps or so. 10 is a safe value.
# scale='iw-mod(iw,2)':'ih-mod(ih,2)' uses scale filter to make sure the output width and height are both divisible by 2 which is a requirement for some encoders. This allows you to use any arbitrarily sized image as an input. Otherwise you can get error: width not divisible by 2.
# format=yuv420p format filter makes output use YUV 4:2:0 chroma subsampling for playback compatibility.
# -movflags +faststart makes the video start playing faster.
# -shortest makes the output as long as audio.mp3. This is needed because -loop 1 was used.
# -fflags +shortest -max_interleave_delta 100M related to -shortest and needed in some cases due to weird behavior by ffmpeg. See My ffmpeg output always add extra 30s of silence at the end for an explanation.

    ffmpeg_command = f""" -loop 1 -framerate 1 -i {image_to_convert_Path} -i {mp3_to_convert_Path} -map 0:v -map 1:a -r 10 -vf "scale='iw-mod(iw,2)':'ih-mod(ih,2)',format=yuv420p" -movflags +faststart -shortest -fflags +shortest -max_interleave_delta 100M {mp4_outfile_Path}"""
    cmd_command = f"{ffmpeg_executable_path} {ffmpeg_command}"

    print(f"input .mp3 file \n {mp3_to_convert_Path}")
    print()
    print(f"input image file \n {image_to_convert_Path}")
    print()
    print(f"output .mp4 file \n {mp4_outfile_Path}")
    print()
    print("cmd prompt command: ")
    print()
    print(cmd_command)

    # call ffmpeg
    returned_value = subprocess.call(
        cmd_command, shell=True
    )  # returns the exit code in unix
    print("returned value:", returned_value)


    # loggin into the channel
    channel = Channel()
    channel.login("client_secret.json", "credentials.storage")


    # setting up the video that is going to be uploaded
    video = LocalVideo(file_path=mp4_outfile_Path)

    # setting snippet
    video.set_title(args.youtube_title)
    video.set_description(args.youtube_description)
    video.set_tags(["this", "tag"])
    video.set_category("people")
    video.set_default_language("fr-FR")

    # setting status
    video.set_embeddable(True)
    video.set_license("youtube")
    video.set_privacy_status("public")
    video.set_public_stats_viewable(True)

    # setting thumbnail
    video.set_thumbnail_path(image_to_convert_Path)

    # not made for kids
    video.set_made_for_kids(False)

    # uploading video and printing the results
    video = channel.upload_video(video)
    print(video.id)
    print(video)


if __name__ == "__main__":
    main()
