FROM python:3.12-slim

# Install Java
RUN apt-get update && apt-get install -y openjdk-11-jre

# Set JAVA_HOME for language_tool_python
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt

# Set the working directory
WORKDIR /app

# Copy the rest of the application
COPY . /app/

# Expose the Streamlit port
EXPOSE 8501

# Start Streamlit app
CMD ["streamlit", "run", "app.py"]
