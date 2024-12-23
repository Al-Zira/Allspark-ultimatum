import os
import subprocess
import pydub
from moviepy.video.io.VideoFileClip import VideoFileClip
from yt_dlp import YoutubeDL

def download_and_merge_ffmpeg(link, output_path="downloads"):
    # Create output directory if it doesn't exist
    os.makedirs(output_path, exist_ok=True)

    # Define output file paths
    video_file = os.path.join(output_path, "temp_video.mp4")
    audio_file = os.path.join(output_path, "temp_audio.m4a")
    output_file = os.path.join(output_path, "final_output.mp4")

    # Download video and audio separately
    ydl_opts_video = {
        "format": "bestvideo[ext=mp4]",
        "outtmpl": video_file,
    }
    ydl_opts_audio = {
        "format": "bestaudio[ext=m4a]",
        "outtmpl": audio_file,
    }

    print("Downloading video...")
    with YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([link])

    print("Downloading audio...")
    with YoutubeDL(ydl_opts_audio) as ydl:
        ydl.download([link])

    # Merge video and audio using ffmpeg
    print("Merging video and audio with ffmpeg...")
    ffmpeg_command = [
        "ffmpeg",
        "-i", video_file,       # Input video file
        "-i", audio_file,       # Input audio file
        "-c:v", "copy",         # Copy video codec without re-encoding
        "-c:a", "aac",          # Use AAC audio codec
        "-strict", "experimental",
        output_file             # Output file
    ]
    subprocess.run(ffmpeg_command)

    # Clean up temporary files
    os.remove(video_file)
    os.remove(audio_file)

    print(f"Downloaded and merged video saved to: {output_file}")
    return output_file

def get_video_duration(input_video):
    # FFprobe command to get video duration
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", input_video
    ]
    
    # Run the command
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Parse the duration
    try:
        duration = float(result.stdout.decode().strip())
        print(f"Video Duration: {duration:.2f} seconds")
        return duration
    except ValueError:
        print("Error: Could not retrieve video duration.")
        return None
def split_video_by_duration(input_video, chunk_duration, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get video duration using FFmpeg
    cmd_duration = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", input_video
    ]
    result = subprocess.run(cmd_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    total_duration = float(result.stdout.decode().strip())

    print(f"Total video duration: {total_duration:.2f} seconds")
    print(f"Splitting into chunks of {chunk_duration} seconds each...")

    # Initialize variables
    chunk_index = 1
    start_time = 0

    # Loop through and split the video
    while start_time < total_duration:
        output_file = os.path.join(output_folder, f"chunk_{chunk_index:03d}.mp4")

        # Calculate the duration for the current chunk
        current_duration = min(chunk_duration, total_duration - start_time)

        cmd_split = [
            "ffmpeg", "-i", input_video, "-ss", str(start_time),
            "-t", str(current_duration), "-c", "copy", output_file
        ]
        subprocess.run(cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Created: {output_file}")

        # Update start time and chunk index
        start_time += chunk_duration
        chunk_index += 1
def clear_folders(directories_to_clear):
    for directory in directories_to_clear:
    # Check if directory exists
        if os.path.exists(directory):
            # Iterate over the files in the directory and remove them
            for file_name in os.listdir(directory):
                file_path = os.path.join(directory, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        print(f"Cleared all files in {directory}")
def adjust_aspect_ratio(input_video, output_video,fill):
    # Desired aspect ratio
    command=None
    if fill:
        command = [
        "ffmpeg",
        "-i", input_video,
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920",
        "-c:v", "libx264",
        "-crf", "23",
        "-preset", "fast",
        "-c:a", "copy",  # Include audio
        output_video
    ]
    else:
        command = [
    "ffmpeg", 
    "-i", input_video,
    "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2", 
    "-c:v", "libx264", 
    "-crf", "23", 
    "-preset", "fast", 
    "-c:a", "copy",  # Include audio, or replace with '-an' to remove
    output_video
    ]

# Execute the command
    subprocess.run(command)

def resize_chunks(folder,outfolder,fill):
    clear_folders([outfolder])
    for filename in os.listdir(folder):
        if filename.endswith(".mp4"):
            input_video = os.path.join(folder, filename)
            output_video = os.path.join(outfolder, f"resized_{filename}")
            adjust_aspect_ratio(input_video,output_video,fill)

if __name__ == "__main__":
    # Input video file

    youtube_link=input("Enter the youtube link: ")
    clear_folders(['downloads'])
    input_video=download_and_merge_ffmpeg(youtube_link)
    print(input_video)
    duration=get_video_duration(input_video)
    print(duration)
    output_folder = "chunks"
    if duration>180:    # Output folder for chunks
    # User selects a duration
        platform=input("Enter Instagram or Youtube: ").lower()
        if platform=='instagram':
            print("Select a duration for splitting (30, 60, 90 seconds):")
        else:
            print("Select a duration for splitting (60, 120, 180 seconds):")
        chunk_duration = int(input("Enter your choice: "))

        if chunk_duration not in [30,60,90,120,180]:
            print("Invalid choice. Please select [30,60,90,120,180] seconds.")
        else:
            clear_folders(['chunks'])
            split_video_by_duration(input_video, chunk_duration, output_folder)
    
    resize_chunks(output_folder, "resized",False)