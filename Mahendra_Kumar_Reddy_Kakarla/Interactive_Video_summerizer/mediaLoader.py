import os
import requests
from pytube import YouTube
import yt_dlp as youtube_dl

class MediaLoader:
    def __init__(self, video_dir=r"media\video"):
        self.video_dir = video_dir
        os.makedirs(self.video_dir, exist_ok=True)

    def save_uploaded_video(self, uploaded_file):
        """
        Saves the uploaded video file to the specified directory.
        """
        video_path = os.path.join(self.video_dir, "uploaded.mp4")
        with open(video_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return video_path

    def download_video_from_link(self, url):
        """
        Downloads video from a given URL using yt-dlp and saves it to the specified directory.
        
        Parameters:
        url (str): The URL of the video to download.

        Returns:
        str: The path of the downloaded video, or None if the download failed.
        """
        video_path = os.path.join(self.video_dir, "downloaded.mp4")  # Specify the output filename

        # Set yt-dlp options
        ydl_opts = {
            'format': 'best',  # Download the best quality
            'outtmpl': video_path,  # Set output path and filename
            'quiet': True  # Suppress verbose output
        }

        # Attempt to download the video
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])  # Pass the URL to yt-dlp for download
            return video_path  # Return the path of the downloaded video

        except Exception as e:
            print(f"Error downloading video: {e}")  # Print any error that occurs
            return None

    def clear_videos(self):
        """
        Deletes all video files in the specified directory.
        """
        for filename in os.listdir(self.video_dir):
            file_path = os.path.join(self.video_dir, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
