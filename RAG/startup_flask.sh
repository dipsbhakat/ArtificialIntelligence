#!/bin/bash

# Go to app directory
cd /home/site/wwwroot

# Install dependencies
pip install --upgrade pip
pip install flask gunicorn

# Debug output
echo "Starting Flask app with Gunicorn on port ${WEBSITES_PORT:-8080}..."
ls -l
echo "Python version: $(python --version)"
echo "Current directory: $(pwd)"
echo "Files:"
ls -l

# Start Flask app with Gunicorn on the correct port
exec gunicorn -b 0.0.0.0:${WEBSITES_PORT:-8080} flask_app:app 2>&1
