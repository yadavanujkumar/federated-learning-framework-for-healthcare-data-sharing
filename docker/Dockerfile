# docker/Dockerfile

# Stage 1: Builder/Compiler
FROM python:3.10-slim as builder

# Metadata
LABEL maintainer="Your Name <your.email@example.com>" \
      description="Federated Learning Framework for Healthcare Data Sharing - Multi-stage Dockerfile" \
      version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    libssl-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy dependency files first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Remove unnecessary files
RUN find . -name '*.pyc' -delete && \
    find . -name '__pycache__' -delete

# Stage 2: Runtime Image
FROM python:3.10-slim

# Metadata
LABEL maintainer="Your Name <your.email@example.com>" \
      description="Federated Learning Framework for Healthcare Data Sharing - Runtime Image" \
      version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libffi7 \
    libssl1.1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser

# Set working directory
WORKDIR /app

# Copy application from builder stage
COPY --from=builder /app /app

# Set proper permissions
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose application port (if applicable)
EXPOSE 8080

# Health check (example: adjust based on your application)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Entrypoint
ENTRYPOINT ["python", "main.py"]