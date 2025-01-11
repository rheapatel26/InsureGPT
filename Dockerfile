# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install Java (OpenJDK)
RUN apt-get update && apt-get install -y openjdk-11-jre-headless

# Set environment variables for Java (optional)
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application files
COPY . .

# Run your app
CMD ["python", "app.py"]
