from moviepy.video.io.VideoFileClip import VideoFileClip
input_video = r"D:\yt_video_downloader\uncharted1.mp4"
output_video = r"D:\yt_video_downloader\uncharted_resized.mp4"

# Desired aspect ratio
desired_aspect_ratio = 9 / 16

# Load the video clip
clip = VideoFileClip(input_video)

# Get the current dimensions
width, height = clip.size
current_aspect_ratio = width / height

# Adjust the clip to match the 9:16 ratio
if current_aspect_ratio > desired_aspect_ratio:  # Too wide, crop width
    new_width = int(height * desired_aspect_ratio)
    crop_width = (width - new_width) // 2
    resized_clip = clip.cropped(x1=crop_width, x2=width - crop_width)
else:  # Too tall, crop height
    new_height = int(width / desired_aspect_ratio)
    crop_height = (height - new_height) // 2
    resized_clip = clip.cropped(y1=crop_height, y2=height - crop_height)

# Resize to standard resolution (optional)
final_clip = resized_clip.resized(height=1920)

# Write the output video
final_clip.write_videofile(output_video, codec="libx264", audio=False)
