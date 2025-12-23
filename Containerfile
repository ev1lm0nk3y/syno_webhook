# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install uv via pip to avoid GHCR auth issues
RUN pip install uv

# Copy project files
COPY pyproject.toml main.py ./
COPY README.md ./

# Install dependencies using uv
# We install the current package in editable mode or just dependencies
# Since we don't have a src layout, installing dependencies directly is safer
RUN uv pip install --system flask paramiko python-dotenv

# Expose the port
EXPOSE 5000

# Run the application
CMD ["python", "main.py"]
