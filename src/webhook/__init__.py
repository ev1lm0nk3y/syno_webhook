from flask import Blueprint, current_app, jsonify, request

from .videos import get_media_file

valid_tokens: list[str] = []

def __init__():
    global valid_tokens
    with current_app.config["TOKEN_FILE"] as tf:
      valid_tokens = tf.read().splitlines()

# Create the blueprint with a url_prefix.
# NOTE: The actual prefix is determined when registering the blueprint in main.py,
# but we can group them here.
bp = Blueprint('webhook', __name__)

@bp.before_request
def validate_request():
    if not request.is_json:
        return jsonify({"status": "error", "message": "Invalid or missing JSON payload"}), 400
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({"status": "error", "message": "Missing token"}), 403
    if token not in valid_tokens:
        return jsonify({"status": "error", "message": "Invalid token"}), 403
    return

# Register the routes from the separate modules
bp.add_url_rule('/sync', view_func=get_media_file, methods=['POST'])

@bp.route('/example1', methods=['POST'])
def example1():
    """
    Example webhook handler 1.
    """
    data = request.json
    print(f"Received example1 webhook with data: {data}")
    return jsonify({"status": "success", "message": "Example 1 executed"}), 200
