from flask import Blueprint, request, jsonify

bp = Blueprint('ebury', __name__)

@bp.route('/callback', methods=['POST'])
def callback():
    data = request.json
    # Process the incoming data from Ebury's API
    # Add your processing logic here

    return jsonify({'status': 'success', 'data': data}), 200