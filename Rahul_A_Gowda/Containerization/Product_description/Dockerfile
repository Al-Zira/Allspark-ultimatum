# Use the official Python 3.9 base image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file to the working directory
COPY requirements.txt requirements.txt

# Install Python dependencies without using cache
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the working directory
COPY product_description.py .

# Mount the secret and make it available for the build process
RUN --mount=type=secret,id=my_secret,target=/run/env/keys \
    echo "Secret value: $(cat /run/env/keys)"

# Command to run the Python application
CMD ["python", "product_description.py"]

#docker build --secret id=GOOGLE_API_KEY,src=credentials.yaml --secret id=USER_NAME,src=credentials.yaml -t rahulagowda04/product_description .
#docker run -i -e GOOGLE_API_KEY=AIzaSyDlVWvKtxMoPST4y2uySiibTiKx9-jkTS8 -e USER_NAME=Rahul rahulagowda04/product_description