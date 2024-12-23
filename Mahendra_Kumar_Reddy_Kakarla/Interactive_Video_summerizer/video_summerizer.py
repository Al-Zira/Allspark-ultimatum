import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
import ffmpeg
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()


class VideoSummerizer:
  def __init__(self):
    self.transcriber=self.load_transcriber_model()
    self.summarizer=self.load_summarizer_model()

  def load_transcriber_model(self):
    """Loads the Whisper Turbo model and returns the pipeline."""

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_id = "openai/whisper-large-v3-turbo"

    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True
    )
    model.to(device)

    processor = AutoProcessor.from_pretrained(model_id)

    pipe = pipeline(
        "automatic-speech-recognition",
        model=model,
        tokenizer=processor.tokenizer,
        feature_extractor=processor.feature_extractor,
        chunk_length_s=30,
        batch_size=16,  # batch size for inference - set based on your device
        torch_dtype=torch_dtype,
        device=device,
        return_timestamps=True
    )

    return pipe

  def transcribe_audio(self,audio_file):
    """Transcribes the given audio file using Whisper Turbo."""
    print("audio transcription start.....!")
    sample = audio_file
    result = self.transcriber(sample)
    return result

  def load_summarizer_model(self):
    """Loads the Gemini Pro model and returns the pipeline."""
    api_key=os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)  # Replace with your actual API key

    model = genai.GenerativeModel('gemini-pro')

    return model

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


  def extract_audio(self,video_path, audio_path="temp_audio.wav"):
    """Extracts the audio from the given video file and saves it as a WAV file."""
    print("audio extraction start.....!")
    try:
        # Use -y to overwrite the output file without asking
        ffmpeg.input(video_path).output(audio_path, format='wav').run(overwrite_output=True, quiet=False)
        return audio_path
    except ffmpeg.Error as e:
        print("Error occurred during audio extraction:")
        print(e.stderr.decode())  # Print the error message
        return None

  def summerize_video(self,video_path):
    """Summerizes the given video file using Whisper Turbo and Gemini Pro."""
    print("video summerizing start.....!")
    audio_path=self.extract_audio(video_path)
    if audio_path is None:
      return None
    print("audio extracted.....!")
    result=self.transcribe_audio(audio_path)
    print("audio transcribed.....!")
    text=result["text"]
    summary=self.summarize_text(text)
    print("text summerized.....!")
    return summary


if __name__ == "__main__":
  summerizer=VideoSummerizer()
  videio_path="/content/drive/MyDrive/Colab Notebooks/Internships2024/Al-Zira-Internship/Interactive_Video_Summerizer/data/Pandas for Data Science in 20 Minutes _ Python Crash Course.mp4"
  summary=summerizer.summerize_video(videio_path)
  print(summary)






