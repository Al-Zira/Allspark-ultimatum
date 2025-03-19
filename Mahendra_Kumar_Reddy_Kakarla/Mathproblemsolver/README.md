Docker CMD:
```sh
docker run -it -e GOOGLE_API_KEY=your_api_key -v .:/app/images ai-math-problem-solver get_answer_from_image              
docker run -it --rm -e GOOGLE_API_KEY=your_api_key ai-math-problem-solver --question="x^2+y^2+2xy=?  x=5" get_answer_for_text 
```
