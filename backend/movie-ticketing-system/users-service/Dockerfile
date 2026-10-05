FROM python:3.12-slim

WORKDIR /app

# Install system dependencies required for psycopg2 and building wheels
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/