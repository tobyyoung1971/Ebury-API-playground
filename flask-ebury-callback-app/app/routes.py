from flask import Blueprint, request, jsonify, redirect, url_for, render_template, Response, current_app, make_response
import requests
from .ebury_api import get_ebury_balance, get_access_token, get_webhook_subscriptions, ping_subscription, delete_webhook_subscription, disable_webhook_subscription, enable_webhook_subscription, get_subscription_types, create_subscription, get_ebury_token, get_clients
from app import socketio
import hmac
import hashlib

bp = Blueprint('ebury', __name__)

# Add health check route
@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'up'}), 200

# Rout for root, home page
@bp.route('/', methods=['GET'])
def root():
    return render_template('index.html')

# Route to get the Ebury login page
@bp.route('/ebo_login', methods=['GET'])
def ebo_login():
    client_id = current_app.config['EBURY_AUTH_CLIENT_ID']
    redirect_uri = current_app.config['EBURY_REDIRECT_URL']
    auth_url = f"{current_app.config['EBURY_AUTHENTICATION_URL']}authenticate?scope=openid&response_type=code&state=state&redirect_uri={redirect_uri}&client_id={client_id}"
    return redirect(auth_url)

# OAuth2 callback route
@bp.route('/auth_callback', methods=['GET'])
def auth_callback():
    code = request.args.get('code')
    if code:
        access_token = get_ebury_token({'code': code})
        if access_token:
            return redirect(url_for('ebury.clients'))
        else:
            return jsonify({'login status': 'failed'}), 400
    else:
        return jsonify({'login status': 'failed', 'error': 'No code provided'}), 400

    
# Add a route to receive callbacks from Ebury's API
@bp.route('/callback', methods=['POST'])
def callback():
    # Extract the JSON payload and signature from the request
    data = request.json
    received_signature = request.headers.get('X-EBURY-SIGNATURE', '')
    if received_signature.startswith("sha3-256="):
        received_hash = received_signature.split("=", 1)[1]
    else:
        received_hash = ""

    # if using a proxy to forward to running on a localhost
    # we need to construct the URL from the headers, because flask
    # will not give us the correct URL scheme behind a proxy
    scheme = request.headers.get('X-Forwarded-Proto', 'https')
    host = request.headers.get('X-Forwarded-Host', request.host)
    path = request.path
    constructed_url = f"{scheme}://{host}{path}"

    # Retrieve the secret for HMAC computation (use an empty string if no secret is set)
    secret = current_app.config.get('EBURY_WEBHOOK_SECRET', '')

    # Construct the payload for HMAC computation
    raw_body = request.data # Get raw body as bytes
    payload = constructed_url.encode('utf-8') + raw_body  # Concatenate URL (encoded) and raw body

    # Compute the expected signature
    computed_hash = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha3_256
    ).hexdigest()

    # Add verification result to the header_info
    header_info = {
        'X_EBURY_CLIENT_ID': request.headers.get('X_EBURY_CLIENT_ID'),
        'X_EBURY_WEBHOOK': request.headers.get('X_EBURY_WEBHOOK'),
        'X_EBURY_SIGNATURE': received_signature,
        'Signature Valid': hmac.compare_digest(received_hash, computed_hash),
    }

    # Merge the header_info into the data object
    data = {
        'header info': header_info,
        **data  # Merge the original data into the new object
    }

    # Debug information
    print("callback headers and data:", data)

    # Push data to the 'callbacks' page using SocketIO
    socketio.emit('new_callback', data)

    return jsonify({'status': 'success', 'X_EBURY_SIGNATURE': received_signature}), 200
 
 # Add a route to display balances for each client_id the login contact has access to.
@bp.route('/balance', methods=['GET'])
def balance():
    balance_info = get_ebury_balance()
    return render_template('balance.html', balances=balance_info)

# Add a route to display webhooks and subscription types
@bp.route('/webhooks', methods=['GET'])
def webhooks():
    webhooks_data = get_webhook_subscriptions()
    return render_template('webhooks.html', webhooks=webhooks_data)

# Add a route to display incoming callbacks
@bp.route('/callbacks', methods=['GET'])
def callbacks():
    return render_template('callbacks.html')

@bp.route('/webhooks/delete/<client_id>/<subscription_id>', methods=['DELETE'])
def delete_webhook(client_id, subscription_id):
    # Use client_id and subscription_id to delete the subscription
    result = delete_webhook_subscription(client_id, subscription_id)
    return jsonify(result)

@bp.route('/webhooks/<action>/<client_id>/<subscription_id>', methods=['PATCH'])
def toggle_webhook(action, client_id, subscription_id):
    if action == 'enable':
        result = enable_webhook_subscription(client_id, subscription_id)
    elif action == 'disable':
        result = disable_webhook_subscription(client_id, subscription_id)
    else:
        return jsonify({'error': 'Invalid action'}), 400
    return jsonify(result)

# Add a route to create a new subscription for a webhook
@bp.route('/subscriptions/new', methods=['GET', 'POST'])
def new_subscription():
    if request.method == 'POST':
        client_id = request.form['client_id']
        url = request.form['url']
        secret = request.form['secret']
        types = request.form.getlist('types')
        result = create_subscription(client_id, url, types, secret)
        return redirect(url_for('ebury.webhooks'))
    
    subscription_types = get_subscription_types()
    enum_values = subscription_types['data']['__type']['enumValues']
    clients_list = get_clients()
    return render_template('new_subscription.html', subscription_types=enum_values, clients=clients_list)

@bp.route('/clients', methods=['GET'])
def clients():
    clients_list = get_clients()
    return render_template('clients.html', clients=clients_list)

@bp.route('/webhooks/ping/<client_id>/<subscription_id>', methods=['POST'])
def ping_webhook(client_id, subscription_id):
    result = ping_subscription(client_id, subscription_id)
    return jsonify(result), 200 if result['status'] == 'success' else 500

# Proxy route to fetch data from Ebury API
# This current only works for the initial graphiql page
# I have not worked out how to proxy the requests made on the page yet
@bp.route('/proxy/ebury_graphql', methods=['GET'])
def proxy_ebury_graphql():
    access_token = get_access_token()
    if not access_token:
        return jsonify({'error': 'Access token not found'}), 401

    # needs to be updated to pass in client_id
    client_id = get_clients()[0].get('client_id')
    url = current_app.config['EBURY_API_URL'] + 'webhooks/'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'X-Client-ID': client_id
    }

    response = requests.get(url, headers=headers)
    return Response(response.content, response.status_code, response.headers.items())

# Show the GraphiQL page supported by Ebury's API
@bp.route('/ebury_graphql', methods=['GET'])
def ebury_graphql():
    return render_template('ebury_graphql.html')