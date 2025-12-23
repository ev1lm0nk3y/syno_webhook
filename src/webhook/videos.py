from typing import Any
from flask import current_app, jsonify, request
import paramiko
import pprint
from os.path import join
import logging
import humanize

logger = logging.getLogger()
def perform_remote_copy(files: list[dict[str, str]]) -> list[str]:
    """Connects via SSH and performs the file operation using current_app config."""
    SSH_HOST = current_app.config.get("SSH_HOST", "")
    SSH_PORT = current_app.config.get("SSH_PORT", 0)
    SSH_USER = current_app.config.get("SSH_USER", "")
    SSH_KEY_PATH = current_app.config.get("SSH_KEY_PATH", "")
    DEST_PATH = current_app.config.get("DEST_PATH", "")

    copy_state = []
    client = paramiko.SSHClient()

    try:
        logger.info(f"Transfering {len(files)} from {SSH_HOST}")
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(
            hostname=SSH_HOST,
            port=SSH_PORT,
            username=SSH_USER,
            key_filename=SSH_KEY_PATH,
        )
        sftp_client = client.open_sftp()

        for src, dest in files:
            copy_state.append((src, None))
            norm_src = sftp_client.normalize(src)
            src_stats = sftp_client.stat(norm_src)
            file_size = src_stats.st_size
            if file_size:
                file_size = humanize.naturalsize(file_size)
            else:
                file_size = "Unknown"
            logger.info(f"{SSH_HOST}:{norm_src} => {dest} [{file_size}]")
            sftp_client.get(norm_src, join(DEST_PATH, dest))
            copy_state[-1][1] = True
    except paramiko.SSHException as e:
        logger.error(f"SSH connection error: {e}")
        raise
    except paramiko.SFTPError as e:
        logger.warning(f"sftp error: {e}")
        copy_state[-1][1] = False
    finally:
        logger.debug("Closing ssh connection")
        client.close()

    return [f for f in copy_state if not f[1]]

def get_media_file():
    """
    Webhook handler that triggers an scp to get a media file.
    """
    payload = request.json
    print(f"Received sync webhook with data: {pprint.pprint(payload)}")

    #success, message = perform_remote_copy()
    success = True

    if success:
        return jsonify({"status": "success", "message": "File copy initiated"}), 200
    else:
        return jsonify({"status": "error", "message": ""}), 500
