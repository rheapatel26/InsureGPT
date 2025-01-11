#!/bin/bash

# Check if Java is available
java -version
if [ $? -ne 0 ]; then
    echo "Java is not available. Exiting."
    exit 1
fi

# Proceed to run the Python application
echo "Java is installed. Starting the application..."
exec "$@"
