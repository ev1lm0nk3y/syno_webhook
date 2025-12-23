import argparse
import logging
import os
import sys

import dotenv
from flask import Flask

from webhook import bp as webhook_bp

# Load env vars from .env file
dotenv.load_dotenv()
logging.basicConfig()
logger = logging.getLogger("synowebhooks")

app = Flask(__name__)

# --- Configuration defaults ---
SSH_HOST = os.getenv("SSH_HOST", "")
SSH_PORT = int(os.getenv("SSH_PORT", "2222"))
SSH_USER = os.getenv("SSH_USER", "")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", os.path.expanduser("~/.ssh/id_rsa"))
DEST_PATH = os.getenv("DEST_PATH", "")
PORT = int(os.getenv("PORT", 5000))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Syno Webhook Listener")
    parser.add_argument("--ssh-host", default=SSH_HOST, help="SSH Hostname")
    parser.add_argument("--ssh-port", default=SSH_PORT, help="SSH Port")
    parser.add_argument("--ssh-user", default=SSH_USER, help="SSH Username")
    parser.add_argument(
        "--ssh-key-path", default=SSH_KEY_PATH, help="Path to SSH private key"
    )
    parser.add_argument(
        "--dest-path", default=DEST_PATH, help="Remote destination path"
    )
    parser.add_argument(
        "--port", default=PORT, type=int, help="Port to run the server on"
    )

    args = parser.parse_args()

    # Store config in app.config so it's accessible to blueprints
    app.config["SSH_HOST"] = args.ssh_host
    app.config["SSH_PORT"] = args.ssh_port
    app.config["SSH_USER"] = args.ssh_user
    app.config["SSH_KEY_PATH"] = args.ssh_key_path
    app.config["DEST_PATH"] = args.dest_path
    app.config["PORT"] = args.port

    # Validate required config
    missing = []
    if not app.config["SSH_HOST"]:
        missing.append("SSH_HOST")
    if not app.config["SSH_USER"]:
        missing.append("SSH_USER")
    if not app.config["DEST_PATH"]:
        missing.append("DEST_PATH")

    if missing:
        print(f"Error: Missing configuration for: {', '.join(missing)}")
        print("Please set them in .env or via command line flags.")
        sys.exit(1)

    # Register the blueprint with the desired prefix
    app.register_blueprint(webhook_bp, url_prefix="/webhook")

    # Run on the configured port
    logger.info(f"Listening on {app.config['PORT']}")
    logger.info(app.url_map)

    app.run(host="0.0.0.0", port=app.config["PORT"])
