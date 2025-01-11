# Start with a Python base image
FROM python:3.11-slim

# Install Java (OpenJDK)
RUN apt-get update && apt-get install -y openjdk-11-jdk

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your Flask app files
COPY . .

# Set the command to run your app
CMD ["python", "app.py"]
