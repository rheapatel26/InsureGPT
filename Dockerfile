# Start with the Python 3.11 slim image
FROM python:3.11-slim

# Install Java (OpenJDK 17) and clean up to reduce image size
RUN apt-get update && apt-get install -y \
    openjdk-17-jdk-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*  # Clean up apt cache to reduce image size

# Set the Java environment variables (just to be sure)
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

# Optionally, verify the Java installation
RUN java -version

# Install Python dependencies (copy requirements.txt first to take advantage of Docker cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the port Flask will run on (this is required by Docker to map the port)
EXPOSE 5000

# Verify if Java is installed (this is useful for debugging)
RUN echo "Java installed at: $JAVA_HOME"

# Set the command to run your app
CMD ["python", "app.py"]
