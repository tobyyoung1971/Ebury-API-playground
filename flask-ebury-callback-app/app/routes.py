from flask import Blueprint, request, jsonify, redirect, url_for

bp = Blueprint('ebury', __name__)

@bp.route('/callback', methods=['POST'])
def callback():
    data = request.json
    # Process the incoming data from Ebury's API
    # Add your processing logic here

    print("Received callback data:", data)

    return jsonify({'status': 'success', 'data': data}), 200

# Add health check route
@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'up'}), 200

@bp.route('/', methods=['GET'])
def root():
    return redirect(url_for('ebury.health_check'))