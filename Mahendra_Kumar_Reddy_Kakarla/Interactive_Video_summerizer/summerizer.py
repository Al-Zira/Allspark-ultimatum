import google.generativeai as genai

class TranscriptProcessor:
    def __init__(self, api_key):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def group_transcripts(self, transcripts, interval=30):
        """
        Groups transcripts into segments based on a specified time interval.
        """
        if not transcripts:
            return []

        # Sort transcripts by start time
        transcripts.sort(key=lambda x: x[0])

        grouped_transcripts = []
        current_group = []
        current_start_time = transcripts[0][0]

        for start_time, text in transcripts:
            # Check if the current start time is within the interval
            if start_time < current_start_time + interval:
                current_group.append(text)
            else:
                # Save the current group and start a new group
                grouped_transcripts.append((current_start_time, " ".join(current_group)))
                current_group = [text]
                current_start_time = start_time

        # Add the last group if it exists
        if current_group:
            grouped_transcripts.append((current_start_time, " ".join(current_group)))

        return grouped_transcripts

    def summarize_with_gemini(self, text):
        """
        Summarizes the given text using the Gemini model with a specific prompt template.
        """
        prompt = (
            "Act as a summarizer. Generate a summary for the following content, "
            "considering that the output size may vary based on the input size. "
            "Be mindful of potential misspellings and incomplete words. "
            "Here is the content:\n\n"
            f"{text}\n\n"
            "Summary:"
        )

        response = self.model.generate_content(prompt)
        return response.text.strip()

    def process_transcript(self, transcripts, interval=30):
        """
        Processes the transcripts: groups them and summarizes each group.
        """
        grouped_transcripts = self.group_transcripts(transcripts, interval)
        summaries = []
        for start_time, group_text in grouped_transcripts:
            summary = self.summarize_with_gemini(group_text)
            summaries.append((start_time, summary))
        return summaries


# Example usage
if __name__ == "__main__":
    api_key = "AIzaSyAgZ618WKny8lEKFSPwMsdxubY5mgNaxgA"  # Set your Google Generative AI API key here
    sorted_transcript =  [
    (0, "let's talk about Python what is it how does it work and how you can get started today all that and more in 2 minutes start the timer"),
    (10, "Python is a problem general purpose programming language often used for machine learning and data analysis Python was created by Guido van Rossum."),
    (20, "Python was first released on February 28, 1991. This language is influential; in 1999, the Zen of Python was released, which is a guiding set of principles for using Python."),
    (30, "There are numerous reasons why this language is popular. The first thing is that Python is very readable and easy to learn."),
    (40, "The Zen of Python states that 'simple is better than complex,' and this reflects the language's philosophy. Python can handle a multitude of tasks from machine learning to data analysis."),
    (50, "Python is widely used in web development, testing, and more. You can download Python from the official getting started with Python page."),
    (60, "Once downloaded, creating a file with Python is as easy as naming the file and ending it with .py. Python files are also referred to as scripts."),
    (70, "If you're interested in web development, my recommendation is either Python or JavaScript; you can't go wrong with either choice."),
    (80, "Python is an interpreted language, which means the source code is converted into bytecode that is then executed by the Python virtual machine."),
    (90, "Python is beginner-friendly, and that's one of the most important reasons to learn it. The language is designed to be easy to understand and use."),
    (100, "Python developers are in high demand; there are currently 36,000 job postings on job platforms for entry-level Python developers."),
    (110, "If you want to learn Python and fully master one of the most relevant languages in the world, consider taking a complete Python developer bootcamp course."),
    (120, "So, whether you are a beginner or looking to enhance your skills, Python is a great choice for a wide range of applications.")
]


    processor = TranscriptProcessor(api_key)
    print(sorted_transcript)
    summaries = processor.process_transcript(sorted_transcript, interval=30)

    for start_time, summary in summaries:
        print(f"Start Time: {start_time}s, Summary: {summary}\n")
