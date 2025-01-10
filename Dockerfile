# Use the latest Python base image
FROM python:3.12-slim

# Set working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# TODO don't do that (just a small hack to avoid SSL errors in my case)
RUN echo insecure >> ~/.curlrc

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy application code
COPY . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app

# Define a build argument for development mode
ARG DEV=false

# TODO delete --allow-insecure-host (just a small hack to avoid SSL errors in my case)
RUN if [ "$DEV" = "true" ]; then \
    uv sync --dev --allow-insecure-host pypi.org --allow-insecure-host files.pythonhosted.org; \
    else \
    uv sync --frozen --allow-insecure-host pypi.org --allow-insecure-host files.pythonhosted.org; \
    fi

ENV PYTHONPATH="/app:$PYTHONPATH"
ENV PATH="/app/.venv/bin:$PATH"
