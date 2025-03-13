# Run in terminal by using this command
docker run -it -e GOOGLE_API_KEY=your_api_key_here db_query_assistant

# your database connection string format will be:
mysql+pymysql://{username}:{password}@host.docker.internal:{port_no.}/{database_name}