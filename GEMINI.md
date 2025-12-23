# syno-webhook

## Project Overview
`syno-webhook` is a Python-based webhook listener designed to trigger remote file operations via SSH. When a POST request is received at the `/webhook` endpoint, the application connects to a configured remote server and executes a file copy command.

## Key Technologies
*   **Python:** Core programming language (>= 3.11).
*   **Flask:** Web framework for handling webhook requests.
*   **Paramiko:** SSHv2 protocol implementation for remote connections.
*   **python-dotenv:** Environment variable management (imported).

## Setup and Installation

### Prerequisites
*   Python 3.11 or higher.
*   SSH access to the target remote server (private key authentication recommended).

### Dependencies
The dependencies are managed via `uv`. To install them:

```bash
uv pip install -r pyproject.toml
# or manually
uv pip install flask paramiko python-dotenv
```

## Configuration
Configuration is managed via environment variables (loaded from a `.env` file) or command-line flags. Command-line flags take precedence over environment variables.

### Environment Variables
Create a `.env` file in the project root with the following variables:

```env
SSH_HOST=your.remote.server.com
SSH_USER=username
SSH_KEY_PATH=~/.ssh/id_rsa
SOURCE_PATH=/path/to/remote/source/file.txt
DEST_PATH=/path/to/remote/destination/
PORT=5000
```

### Command-Line Flags
You can override configuration using the following flags:

*   `--ssh-host`: Remote server hostname.
*   `--ssh-user`: SSH username.
*   `--ssh-key-path`: Path to your private SSH key.
*   `--source-path`: Path to the source file on the remote server.
*   `--dest-path`: Destination path on the remote server.
*   `--port`: Port to run the server on (default: 5000).

## Running the Application
To start the webhook listener (development mode):

```bash
# Using .env configuration
python main.py

# Overriding with flags
python main.py --port 8080 --ssh-host 192.168.1.100
```

The server will start on `http://0.0.0.0:5000`.

## Usage
Trigger the webhook by sending a POST request:

```bash
curl -X POST http://localhost:5000/webhook -H "Content-Type: application/json" -d '{"key": "value"}'
```

## Development Notes
*   **Security:** The current implementation uses `paramiko.AutoAddPolicy()`, which is not recommended for production as it is susceptible to Man-in-the-Middle (MitM) attacks.
*   **Deployment:** The built-in Flask server is for development only. Use a production WSGI server like Gunicorn for deployment.

## Agent Guidelines
*   **Minimalism:** Do not create excessive tests, documentation, or random scripts unless explicitly requested or absolutely necessary for a critical verification that cannot be done otherwise.
*   **Focus:** Stick strictly to the user's requested task. Avoid proactive "cleanup" or "enhancement" unless it directly addresses the core issue.