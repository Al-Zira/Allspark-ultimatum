import os
import time
import asyncio
import edge_tts
import subprocess
import random
from pydub.utils import mediainfo
from dotenv import load_dotenv
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

class LanguageModelProcessor:
    def __init__(self):
        # Initialize the language model (Groq)
        self.llm = ChatGroq(
            temperature=0.7,  # Adjusted for creativity
            model_name="llama3-groq-70b-8192-tool-use-preview",
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.conversation = None  # Placeholder for the conversation chain

    def create_system_prompt(self, topic):
        # System prompt setup for generating a narrated story
        system_prompt = f"""

        Topic: {topic}

        You are a creative assistant specialized in writing scripts for Youtube shorts and instagram reels generation.
        Your task is to create a captivating story based on the given topic.
        The story length should be less than 180 seconds even after the audio generation for this story accordingly adjust the story length.
        The story content shold be adjust based duration and it will perfectly fit in audio generation.
        It should be engaging, clear, and follow a storytelling format.
        it should have only story lines not any other beacuse the text directly converted into audio using some tts model so it should be clear and easy to understand by the listener.
        The story should be about the {topic} genre and should be suitable for a young audience.
        The story should start without any inroduction statements .
        The story should be very short and concise, with a clear beginning, middle, and end. Avoid unnecessary details and keep the language simple and easy to understand.

        
        """

        # Define the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(system_prompt),
            HumanMessagePromptTemplate.from_template("{text}")
        ])

        # Create the conversation chain
        self.conversation = LLMChain(
            llm=self.llm,
            prompt=self.prompt
        )

    def process_user_message(self, user_message):
        start_time = time.time()
        response = self.conversation.invoke({"text": user_message})
        end_time = time.time()

        response_time = end_time - start_time
        return response, response_time
    def crop_for_short(self, input_video, output_video, desired_duration):
        result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", input_video],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
        )
        video_duration = float(result.stdout.strip())

        # Ensure the desired duration does not exceed the video length
        if desired_duration > video_duration:
            raise ValueError("Desired duration exceeds the video length.")

        # Generate a random starting point
        start_time = random.uniform(0, video_duration - desired_duration)

        # Use ffmpeg to crop the video segment
        command = [
            "ffmpeg",
            "-ss", str(start_time),       # Start time
            "-i", input_video,            # Input file
            "-t", str(desired_duration),  # Duration
            "-c:v", "copy",               # Copy video codec (fast, no re-encoding)
            "-c:a", "copy",               # Copy audio codec (fast, no re-encoding)
            "-y",                         # Force overwrite
            output_video                  # Output file
        ]


        # Run the command
        subprocess.run(command, check=True)

        print(f"Cropped video saved to: {output_video}")
    def merge_video_audio(self,video_path, audio_path, output_path):
        # FFmpeg command to merge video and audio
        command = [
            'ffmpeg',
            '-i', video_path,  # Input video file
            '-i', audio_path,  # Input audio file
            '-c:v', 'copy',     # Copy the video codec
            '-c:a', 'aac',      # Encode audio in AAC format
            '-strict', 'experimental',  # Allow experimental codecs
            output_path         # Output file
        ]

        # Run the command
        subprocess.run(command, check=True)

    async def save_speech(self,text, filename,  voice="af-ZA-AdriNeural"):
        communicator = edge_tts.Communicate(text=text, voice=voice)
        await communicator.save(filename)

    def text_to_speech(self,text, voice="af-ZA-AdriNeural"):
        filename = "output.mp3"

        asyncio.run(self.save_speech(text, filename,  voice))

        return filename


# Usage Example
if __name__ == "__main__":
    processor = LanguageModelProcessor()


    topics=["Horror",
        "Comedy",
        "Adventure",
        "Romance",
        "Sci-Fi",
        "Mystery",
        "Fantasy",
        "Thriller",
        "Historical",
        "Drama"]
    # User inputs for topic and duration
    topic = input("1.Horror\n2.Comedy\n3.Adventure\n4.Romance\n5.Sci-Fi\n6.Mystery\n7.Fantasy\n8.Thriller\n9.Historical\n10.Drama\nEnter the topic: ")
    topic=topics[int(topic)-1]
    print(topic)


    # Create the system prompt
    processor.create_system_prompt(topic=topic)

    # Generate and display the story script
    user_message = "Generate the narrated story script."
    bot_response, response_time = processor.process_user_message(user_message)

    print(f"Generated Story :\n{bot_response['text']}")

    # Convert the story script to speech
    filename = processor.text_to_speech(bot_response['text'])

    info = mediainfo(filename)
    
    # Retrieve the duration in seconds
    duration = float(info['duration'])
    # print("duration:",duration)

    # input_video=r"samplevideos\ratio916\output_video.mp4"
    # output_video=r"shorts\short_video.mp4"

    # processor.crop_for_short(input_video,output_video,duration)
    # processor.merge_video_audio(output_video,filename,r"shorts\final_short_video.mp4")
    print("audio output stored here:",filename)

    print(f"\nResponse Time: {response_time:.2f} seconds")
