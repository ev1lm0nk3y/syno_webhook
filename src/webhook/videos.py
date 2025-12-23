import logging
import pprint
import threading
from os import makedirs
from os.path import dirname, exists, join

import humanize
import paramiko
from flask import current_app, jsonify, request

logger = logging.getLogger()

def perform_remote_copy(src: str, dst: str, config: dict) -> bool:
    """Connects via SSH and performs the file operation using provided config."""
    SSH_HOST = config.get("SSH_HOST", "")
    SSH_PORT = config.get("SSH_PORT", 0)
    SSH_USER = config.get("SSH_USER", "")
    SSH_KEY_PATH = config.get("SSH_KEY_PATH", "")

    client = paramiko.SSHClient()

    try:
        logger.info(f"Transfering {src} from {SSH_HOST}")
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            key_filename=SSH_KEY_PATH,
        )
        sftp_client = client.open_sftp()

        norm_src = sftp_client.normalize(src)
        src_stats = sftp_client.stat(norm_src)
        file_size = src_stats.st_size
        if file_size:
            file_size = humanize.naturalsize(file_size)
        else:
            file_size = "Unknown"
        logger.info(f"{SSH_HOST}:{norm_src} => {dst} [{file_size}]")
        if not exists(dirname(dst)):
            makedirs(dirname(dst))
        sftp_client.get(norm_src, dst)
        logger.info(f"{dst} copied successfully")
        return True
    except paramiko.SSHException as e:
        logger.error(f"SSH connection error: {e}")
    except paramiko.SFTPError as e:
        logger.error(f"sftp error: {e}")
    except Exception as e:
        logger.exception(f"Unexpected error during remote copy: {e}")
    finally:
        logger.debug("Closing ssh connection")
        client.close()
    return False

def _background_copy_task(src, dst: str, config: dict):
    """Wrapper to run copy in background and log results."""
    try:
        failed_files = perform_remote_copy(src, dst, config)
        if failed_files:
            logger.error(f"Failed to copy the following files: {failed_files}")
        else:
            logger.info("Background file copy completed successfully.")
    except Exception as e:
        logger.exception(f"Background task failed: {e}")

def get_media_file():
    """
    Webhook handler that triggers an scp to get a media file.
    """
    payload = request.get_json(silent=True)
    logger.debug(f"Received sync webhook with data: {pprint.pformat(payload)}")

    config = {
        "SSH_HOST": current_app.config.get("SSH_HOST"),
        "SSH_PORT": current_app.config.get("SSH_PORT"),
        "SSH_USER": current_app.config.get("SSH_USER"),
        "SSH_KEY_PATH": current_app.config.get("SSH_KEY_PATH"),
    }

    match payload["eventType"]:
      case "Download":
        anime_or_tv = "Anime" if payload["series_type"] == "Anime" else "TV Shows"
        dst_file_path = join(
          current_app.get("DEST_PATH", ""),
          anime_or_tv,
          payload["series"]["title"],
          payload["episodeFile"]["path"].split("/")[-1],
        )
        # Run in background
        thread = threading.Thread(
          target=_background_copy_task,
          args=(payload["episodeFile"]["path"], dst_file_path, config))
        thread.start()
      case _:
        logger.warning(f"Unknown event type: {payload['event_type']}")
        return jsonify({"status": "unknown", "message": "webhook operation unknown"}), 404

    return jsonify({"status": "success", "message": "File copy initiated in background"}), 202
