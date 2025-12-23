# Use a lightweight Python base image
FROM python:3.13-slim

ARG PUID=1000
ARG PGID=1000
ARG USER=app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Copy project files
COPY * ./

# Install uv via pip to avoid GHCR auth issues
RUN adduser --uid $PUID --gecos --gid $PGID --disabled-password $USER && \
    pip install --root-user-action ignore uv && \
	uv pip install --system --no-cache --link-mode hardlink -r requirements.txt

USER $USER

# Run the application
CMD ["python", "main.py"]
