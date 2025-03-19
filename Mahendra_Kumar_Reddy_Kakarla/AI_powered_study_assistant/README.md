Docker CMD:
```sh
docker run -it -e GOOGLE_API_KEY=your_api_key ai-study-assistant text_summary --input "Your text here." --prompt "Summarize this text concisely." 
docker run -it -e GOOGLE_API_KEY=your_api_key -v .:/app/images ai-study-assistant image_summary --prompt "Describe the images in detail."
docker run -it -e GOOGLE_API_KEY=your_api_key ai-study-assistant generate_test_and_evaluate --input "Artificial Intelligence and its applications in healthcare."
docker run -it -e GOOGLE_API_KEY=your_api_keyai-study-assistant find_resources --input "AI Agents"
```
