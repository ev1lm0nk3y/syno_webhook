from flask import Blueprint, jsonify, request
from .videos import get_media_file

# Create the blueprint with a url_prefix. 
# NOTE: The actual prefix is determined when registering the blueprint in main.py,
# but we can group them here.
bp = Blueprint('webhook', __name__)

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


