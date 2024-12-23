import os
import subprocess
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


def split_video(input_video, num_parts, output_folder):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get video duration using FFmpeg
    cmd_duration = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration", 
        "-of", "default=noprint_wrappers=1:nokey=1", input_video
    ]
    result = subprocess.run(cmd_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    total_duration = float(result.stdout.decode().strip())
    
    # Calculate duration of each part
    part_duration = total_duration / num_parts

    # Split the video into parts
    for i in range(num_parts):
        start_time = i * part_duration
        output_file = os.path.join(output_folder, f"part_{i + 1:03d}.mp4")

        cmd_split = [
            "ffmpeg", "-i", input_video, "-ss", str(start_time),
            "-t", str(part_duration), "-c", "copy", output_file
        ]
        subprocess.run(cmd_split, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Created: {output_file}")

# Example usage
split_video(r"downloads\final_output.mp4", 5, "chunks")

# # Example usage
# download_and_merge_ffmpeg("https://www.youtube.com/watch?v=9pEqyr_uT-k")
