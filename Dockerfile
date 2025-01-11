# Start with a Python base image
FROM python:3.11-slim

# Install Java (OpenJDK 11) and utilities to check the installation
RUN apt-get update && apt-get install -y \
    openjdk-11-jdk \
    && apt-get clean \
    && java -version \
    && javac -version  # Verify that Java is installed

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install OpenJDK (Java)
RUN apt-get update && \
    apt-get install -y openjdk-11-jre

# Copy the Flask app files
COPY . .

# Set the command to run your app
CMD ["python", "app.py"]
