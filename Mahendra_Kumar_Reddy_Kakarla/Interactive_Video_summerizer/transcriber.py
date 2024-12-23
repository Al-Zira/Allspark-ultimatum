import os
import speech_recognition as sr
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor, as_completed

class AudioTranscriber:
    def __init__(self, file_path, chunk_length_ms=30000, output_dir='chunks'):
        self.file_path = file_path
        self.chunk_length_ms = chunk_length_ms
        self.output_dir = output_dir
        self.recognizer = sr.Recognizer()

    def convert_to_mono(self):
        """Convert audio file to mono."""
        audio = AudioSegment.from_file(self.file_path)
        mono_audio = audio.set_channels(1)  # Convert to mono
        # Ensure the audio has a proper frame size
        if len(mono_audio) % 1000 != 0:
            mono_audio = mono_audio[:len(mono_audio) - (len(mono_audio) % 1000)]
        return mono_audio

    def split_audio(self, audio):
        """Split audio into chunks of specified length."""
        chunks = []
        for i in range(0, len(audio), self.chunk_length_ms):
            chunk = audio[i:i + self.chunk_length_ms]
            if len(chunk) > 0:  # Ensure the chunk is not empty
                chunks.append((chunk, i))  # Append tuple (chunk, start_time)
        return chunks

    def save_chunks(self, chunks):
        """Save audio chunks to the specified directory."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        chunk_paths = []
        for i, (chunk, start_time) in enumerate(chunks):
            chunk_file_path = os.path.join(self.output_dir, f'chunk_{i}.wav')
            chunk.export(chunk_file_path, format='wav')
            chunk_paths.append((chunk_file_path, start_time))  # Append tuple (path, start_time)
        return chunk_paths

    def transcribe_audio(self, file_path, start_time):
        """Transcribe audio using Google Web Speech API and return with timestamp."""
        with sr.AudioFile(file_path) as source:
            audio_data = self.recognizer.record(source)
        try:
            text = self.recognizer.recognize_google(audio_data, language="en-US")
            return (start_time // 1000, text)  # Return start_time in seconds and text
        except sr.UnknownValueError:
            return (start_time // 1000, "Could not understand audio.")
        except sr.RequestError as e:
            return (start_time // 1000, f"Could not request results; {e}")

    def process_audio(self):
        """Process the audio file by splitting it into chunks and transcribing each chunk."""
        # Convert to mono
        mono_audio = self.convert_to_mono()
        chunks = self.split_audio(mono_audio)
        chunk_paths = self.save_chunks(chunks)
        transcript_data=[]
        # Transcribe each chunk using batch processing
        with ThreadPoolExecutor() as executor:
            future_to_chunk = {executor.submit(self.transcribe_audio, path, start_time): (path, start_time) for path, start_time in chunk_paths}

            for future in as_completed(future_to_chunk):
                start_time, transcript = future.result()  # Get results
                transcript_data.append((start_time,transcript))
                # Print the transcription immediately with its timestamp
                print(f"Start Time: {start_time}s, Transcript: {transcript}")
        return transcript_data

# Example usage
if __name__ == "__main__":
    audio_file_path = 'temp_audio1.wav'  # Replace with your audio file path
    transcriber = AudioTranscriber(audio_file_path, chunk_length_ms=10000)  # 10 seconds chunks
    transcript=transcriber.process_audio()

    # Sort the transcript data by the start time
    sorted_transcript = sorted(transcript, key=lambda x: x[0])

    # Display the sorted transcript
    for start_time, transcript in sorted_transcript:
        print(f"Start Time: {start_time}s, Transcript: {transcript}")