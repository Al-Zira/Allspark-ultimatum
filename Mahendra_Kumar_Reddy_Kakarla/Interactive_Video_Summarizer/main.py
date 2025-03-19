import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import ffmpeg
import google.generativeai as genai
import os
import yt_dlp
import argparse
from dotenv import load_dotenv
load_dotenv()

class VideoSummerizer:
  def __init__(self):
    self.transcriber=self.load_transcriber_model()
    self.api_key=self._load_api_key()
    self.summarizer=genai.GenerativeModel("gemini-2.0-flash")

  def _load_api_key(self) -> str:
        """Load API key from environment variables."""
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return api_key
  
  def download_video(self,url, output_path="./videos"):
    os.makedirs(output_path, exist_ok=True)  # Ensure directory exists

    ydl_opts = {
        'format': 'bv*+ba/best',  # Best video + best audio, fallback to best
        'outtmpl': os.path.join(output_path, 'temp_video.%(ext)s'),  # Keeps correct extension
        'merge_output_format': 'mp4',  # Ensures final file is MP4
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # Converts to MP4 if needed
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return os.path.join(output_path, 'temp_video.mp4') 


  def load_transcriber_model(self):
    """Loads the Whisper Turbo model from the locally saved folder and returns the pipeline."""

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_path = "./local_model"
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_path, torch_dtype=torch_dtype, low_cpu_mem_usage=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_path)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=30,
        batch_size=16,  # Adjust batch size based on your device
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True
    )
    print("loading transcriber completed....!")
    return pipe


  def transcribe_audio(self,audio_file):
    """Transcribes the given audio file using Whisper Turbo."""
    print("audio transcription start.....!")
    sample = audio_file
    result = self.transcriber(sample)
    return result

  def summarize_text(self,text):
    """Summarizes the given text using Gemini Pro.

    Args:
      text: The text to summarize.

    Returns:
      A summary of the text in bullet points.
    """
    print("text summerizing start.....!")

    prompt = f"""
      Summarize the following text:

      {text}
    """

    response = self.summarizer.generate_content(prompt)
    summary = response.text

    return summary


  def extract_audio(self, video_path, audio_path=None):
    audio_dir = "./audios"
    os.makedirs(audio_dir, exist_ok=True)
    if audio_path is None:
        audio_path = os.path.join(audio_dir, "temp_audio.wav")
    try:
        ffmpeg.input(video_path).output(audio_path, format='wav').run(overwrite_output=True, quiet=True)
        return audio_path
    except ffmpeg.Error as e:
        print("Error occurred during audio extraction:", e.stderr.decode())
        return None

  
     
  def summarize_video(self, youtube_link=None):
    """Summarizes the given video."""
    print("Video summarization started...")
    
    video_path = None

    if youtube_link:
        self.download_video(youtube_link)
        

    if not video_path:  # If no YouTube link was given, use a local file
        video_dir = "./videos"
        video_files = [f for f in os.listdir(video_dir) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
        if video_files:
            video_path = os.path.join(video_dir, video_files[0])
        else:
            print("No video files found.")
            return None

    print(f"Processing video: {video_path}")

    audio_path = self.extract_audio(video_path)
    if not audio_path:
        return None

    print("Audio extracted...")
    transcription = self.transcribe_audio(audio_path)
    print("Audio transcribed...")

    text = transcription.get("text", "")
    if not text:
        print("No text extracted.")
        return None

    summary = self.summarize_text(text)
    print("Text summarized!")
    return summary

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Interactive video summarizer")
    parser.add_argument("--youtube_link", type=str, help="Enter YouTube link (optional)", default=None)

    args = parser.parse_args()

    summarizer = VideoSummerizer()

    if args.youtube_link:  # Fix incorrect attribute reference
        summary = summarizer.summarize_video(args.youtube_link)
    else:
        summary = summarizer.summarize_video()

    print(summary)






