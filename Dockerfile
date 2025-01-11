# Start with the Python 3.11 slim image
FROM python:3.11-slim

# Install Java (OpenJDK 17)
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Set the Java environment variables (just to be sure)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Optionally, verify the Java installation
RUN java -version

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Check if Java is installed and print path
RUN echo "Java installed at: $JAVA_HOME"

# Run your app
CMD ["python", "app.py"]
