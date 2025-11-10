# backend/Dockerfile

# 1. Use the official lightweight Python image as a base
FROM python:3.11-slim

# 2. Set the working directory
WORKDIR /app

# 3. Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 4. Copy and install Python requirements FIRST
# We need playwright installed before we can ask it to install its own dependencies.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. (THE DEFINITIVE FIX) Use Playwright's own tool to install ALL system dependencies
# This command connects to Playwright's servers, gets the correct list of packages
# for this specific OS version, and installs them with apt-get.
RUN playwright install-deps

# 6. (THE PERMANENT FIX) Install the browser binaries into the image itself
RUN playwright install
# 6. Copy the application source code
COPY ./app /app/

# 7. Expose the service port
EXPOSE 8000