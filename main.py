from flask import Flask, request, jsonify
import paramiko
import os
import dotenv
import logging

import sys
import argparse

# Load env vars from .env file
dotenv.load_dotenv()

app = Flask(__name__)

# --- Configuration ---
# Defaults from environment variables or hardcoded fallbacks
SSH_HOST = os.getenv("SSH_HOST")
SSH_USER = os.getenv("SSH_USER")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", os.path.expanduser("~/.ssh/id_rsa"))
SOURCE_PATH = os.getenv("SOURCE_PATH")
DEST_PATH = os.getenv("DEST_PATH")
PORT = int(os.getenv("PORT", 5000))

def remote_copy():
    """Connects via SSH and performs the file operation."""
    try:
        client = paramiko.SSHClient()
        # Automatically add the remote host key (use with caution in production)
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Connect using key-based authentication
        client.connect(hostname=SSH_HOST, username=SSH_USER, key_filename=SSH_KEY_PATH)
        
        # Example: Copying a file on the remote host itself
        # You could also use SCPClient to move files FROM local TO remote
        command = f"cp {SOURCE_PATH} {DEST_PATH}"
        stdin, stdout, stderr = client.exec_command(command)
        
        error = stderr.read().decode()
        if error:
            return False, error
            
        client.close()
        return True, "Success"
    except Exception as e:
        return False, str(e)

@app.route('/webhook', methods=['POST'])
def webhook_listener():
    # You can inspect the payload from the webhook here
    data = request.json
    print(f"Received webhook with data: {data}")

    # Trigger the SSH operation
    success, message = remote_copy()

    if success:
        return jsonify({"status": "success", "message": "File copy initiated"}), 200
    else:
        return jsonify({"status": "error", "message": message}), 500

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Syno Webhook Listener")
    parser.add_argument("--ssh-host", default=SSH_HOST, help="SSH Hostname")
    parser.add_argument("--ssh-user", default=SSH_USER, help="SSH Username")
    parser.add_argument("--ssh-key-path", default=SSH_KEY_PATH, help="Path to SSH private key")
    parser.add_argument("--source-path", default=SOURCE_PATH, help="Remote source path")
    parser.add_argument("--dest-path", default=DEST_PATH, help="Remote destination path")
    parser.add_argument("--port", default=PORT, type=int, help="Port to run the server on")

    args = parser.parse_args()

    # Update globals with command line args (if provided/overridden)
    SSH_HOST = args.ssh_host
    SSH_USER = args.ssh_user
    SSH_KEY_PATH = args.ssh_key_path
    SOURCE_PATH = args.source_path
    DEST_PATH = args.dest_path
    PORT = args.port

    # Validate required config
    missing = []
    if not SSH_HOST: missing.append("SSH_HOST")
    if not SSH_USER: missing.append("SSH_USER")
    if not SOURCE_PATH: missing.append("SOURCE_PATH")
    if not DEST_PATH: missing.append("DEST_PATH")
    
    if missing:
        print(f"Error: Missing configuration for: {', '.join(missing)}")
        print("Please set them in .env or via command line flags.")
        sys.exit(1)

    # Run on port 5000 - Use a production server like Gunicorn for deployment
    app.run(host='0.0.0.0', port=PORT)
