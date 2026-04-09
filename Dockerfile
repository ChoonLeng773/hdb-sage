# Builder
# Using bookworm (Debian 12) for better compatibility with newer chromadb requirements
FROM python:3.11-slim-bookworm AS builder
# I used 3.14 when developing , test if there is an issue


# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build

# dependencies
# Required for compiling packages like grpcio, bcrypt, and chromadb dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment for isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install requirements
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# STAGE 2: Final Runtime
FROM python:3.11-slim-bookworm AS final

# Standardize working directory
WORKDIR /app

COPY --from=builder /opt/venv /opt/venv

# Ensure the app uses the virtual environment
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app/src" \
    # ChromaDB/SQLite compatibility fix for older systems if necessary
    IS_DOCKER=True

# copy source code
COPY . .

# Ollama port : 11400
EXPOSE 11401

# chat.py is the chatting application with the cli
CMD ["python", "src/chat.py"]