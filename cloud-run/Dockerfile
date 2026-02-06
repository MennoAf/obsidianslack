# Use official Python runtime as base image
# Pinned to specific version for reproducibility
# Update periodically: https://hub.docker.com/_/python
FROM python:3.11.8-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for Obsidian vault (will be mounted or synced)
RUN mkdir -p /vault

# Set environment variable for Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Expose port (Cloud Run will set PORT env variable)
ENV PORT=8080
EXPOSE 8080

# Run as non-root user
RUN useradd -m appuser
USER appuser

# Run the application
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 main:app
