# backend/Dockerfile

# =================================================================================
# Stage 1: Build a base image with all system and browser dependencies
# This stage will only re-run if the base image itself changes (very rare).
# =================================================================================
FROM python:3.11-slim AS builder-base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnspr4 libnss3 libdbus-1-3 libexpat1 libxcb1 libxkbcommon0 libasound2 \
    libatk1.0-0 libatk-bridge2.0-0 libatspi2.0-0 libcups2 libx11-6 libxcomposite1 \
    libxdamage1 libxext6 libxfixes3 libxrandr2 libgbm1 libcairo2 libpango-1.0-0 \
    libxcursor1 libgtk-3-0 libpangocairo-1.0-0 libcairo-gobject2 libgdk-pixbuf-xlib-2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies needed for playwright install
# We only install playwright here to keep this layer small and stable.
RUN pip install playwright

# Install playwright system dependencies
RUN playwright install-deps

# Install browser binaries
RUN playwright install


# =================================================================================
# Stage 2: Build the final application image
# This stage uses the builder-base and will be much faster.
# =================================================================================
FROM builder-base

# Set the working directory
WORKDIR /app

# Copy the Python requirements file
COPY requirements.txt .

# Install Python requirements
# This will use the pip_cache volume we defined in docker-compose.yml
# It will be very fast after the first run.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
# This is done last, as it's the most frequently changing part.
COPY ./app /app/

# Expose the service port
EXPOSE 8000