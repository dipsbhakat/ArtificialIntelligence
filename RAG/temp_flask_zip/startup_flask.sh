#!/bin/bash

# Go to app directory
cd /home/site/wwwroot

# Install dependencies
pip install --upgrade pip
pip install flask

# Start Flask app on the correct port
echo "Starting Flask app on port ${WEBSITES_PORT:-8080}..."
exec python flask_app.py
