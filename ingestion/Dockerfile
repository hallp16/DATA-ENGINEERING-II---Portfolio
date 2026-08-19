# ---------------------------------------------------------------------
# Ingestion Service Dockerfile
# Base Image: Python 3.9 slim to minimize container size and security attack surface
# ---------------------------------------------------------------------
FROM python:3.9.18-slim

# Set working directory inside the container
WORKDIR /app

# Docker Layer Caching Best Practice:
# Copy requirements first to avoid reinstalling dependencies when only code changes
COPY requirements.txt .

# Install Python packages without caching installation files to keep image lightweight
RUN pip install --no-cache-dir -r requirements.txt

# Copy the ingestion script into the container
COPY ingest.py .

# Entry point: run the batch ingestion script automatically on startup
CMD ["python", "ingest.py"]