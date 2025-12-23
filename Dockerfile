# Use a lightweight Python base image
FROM python:3.13-slim

ARG PUID=1000
ARG PGID=1000
ARG USER=app
ARG GROUP=appgroup

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /app && chmod 777 /app && \
    addgroup --gid $PGID $GROUP && \
    adduser --uid $PUID --gecos --gid $PGID --disabled-password $USER && \
    pip install --no-cache-dir --root-user-action ignore uv

WORKDIR /app
COPY * /app

RUN uv pip install --system --no-cache --link-mode hardlink -r requirements.txt

USER $USER

# Run the application
CMD ["python", "main.py"]
