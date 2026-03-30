# ./Dockerfile

# Start with a slim and efficient Python base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the Python dependencies
# --no-cache-dir reduces the image size
RUN pip install --no-cache-dir -r requirements.txt

# NOTE: Your project uses a custom 'mcp' library.
# If this is a private package, you must add steps here to install it.
# For example, if it's a wheel file:
# COPY ./path/to/mcp-wheel.whl /tmp/
# RUN pip install /tmp/mcp-wheel.whl

# Create directories for logs and the ChromaDB database.
# This ensures the directories exist within the container.
RUN mkdir -p /app/logs /app/chroma_db

RUN pip install mcp

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js (which includes npm and npx)
# This uses the NodeSource script to add the Node.js repository and then installs it via apt
# You can replace '20.x' with the desired Node.js version (e.g., '22.x', '18.x')
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Verify Node.js, npm, and npx installations
RUN node -v
RUN npm -v
RUN npx -v

# Copy the entire project directory into the container's working directory
COPY . .
COPY .env.sandbox .env
COPY config.json.sandbox config.json