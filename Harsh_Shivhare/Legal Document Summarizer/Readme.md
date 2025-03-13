# Run in terminal by using this command
docker run -it --dns 8.8.8.8 --dns 8.8.4.4 -v {file_path}:/app -e GOOGLE_API_KEY="your_api_key" legal_doc_summarizer


# File path will be given as 
/app/{file_name}.pdf