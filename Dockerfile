# Use an official Python base image
FROM python:3.11-slim

# Install system dependencies (including Java)
RUN apt-get update && \
    apt-get install -y openjdk-11-jre && \
    apt-get clean && \
    java -version  # This will verify that Java is installed

# Set JAVA_HOME environment variable
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Set the working directory in the container
WORKDIR /app

# Copy the requirements.txt and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . /app/

# Command to run your application
CMD ["python", "app.py"]
