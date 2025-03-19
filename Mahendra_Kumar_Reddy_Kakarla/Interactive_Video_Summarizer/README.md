Docker CMD:
```sh
docker -run -it --rm -e GOOGLE_API_KEY=your_api_key -v $(pwd)/videos:/app/videos ai-video-summarizer
docker -run -it --rm -e GOOGLE_API_KEY=your_api_key --youtube_link "your_youtube_link" ai-video-summarizer
```
