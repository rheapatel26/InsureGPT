# Start with the Python 3.11 slim image
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size


# Optionally, verify the Java installation
RUN java -version

# Continue with the rest of your Dockerfile...


# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Run your app
CMD ["python", "app.py"]
