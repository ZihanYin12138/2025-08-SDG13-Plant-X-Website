# Use Python 3.11 as base image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libspatialindex-dev \
    libgeos-dev \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY 04_epic7_backend_sql.py .

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=04_epic7_backend_sql.py
ENV FLASK_ENV=production

# Startup command
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "04_epic7_backend_sql:app"]


