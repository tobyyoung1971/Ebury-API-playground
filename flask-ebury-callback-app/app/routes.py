from flask import Blueprint, request, jsonify, redirect, url_for, render_template
from .ebury_api import get_ebury_balance, get_webhook_subscriptions, delete_webhook_subscription, disable_webhook_subscription, get_subscription_types, create_subscription
from app import socketio

bp = Blueprint('ebury', __name__)

@bp.route('/callback', methods=['POST'])
def callback():
    data = request.json
    # Process the incoming data from Ebury's API
    # Add your processing logic here

    print("Received callback data:", data)
    socketio.emit('new_callback', data) 
    return jsonify({'status': 'success', 'data': data}), 200

# Add health check route
@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'up'}), 200

@bp.route('/', methods=['GET'])
def root():
    return render_template('index.html')
#   return redirect(url_for('ebury.health_check'))
 
@bp.route('/balance', methods=['GET'])
def balance():
    balance_info = get_ebury_balance()
    return render_template('balance.html', balance=balance_info)

@bp.route('/webhooks', methods=['GET'])
def webhooks():
    subscriptions = get_webhook_subscriptions()
    return render_template('webhooks.html', subscriptions=subscriptions)

@bp.route('/callbacks', methods=['GET'])
def callbacks():
    return render_template('callbacks.html')

@bp.route('/webhooks/delete/<subscription_id>', methods=['DELETE'])
def delete_webhook(subscription_id):
    result = delete_webhook_subscription(subscription_id)
    return jsonify(result)

@bp.route('/webhooks/disable/<subscription_id>', methods=['PATCH'])
def disable_webhook(subscription_id):
    result = disable_webhook_subscription(subscription_id)
    return jsonify(result)

@bp.route('/subscriptions/new', methods=['GET', 'POST'])
def new_subscription():
    if request.method == 'POST':
        url = request.form['url']
        secret = request.form['secret']
        types = request.form.getlist('types')
        result = create_subscription(url, types, secret)
        return redirect(url_for('ebury.webhooks'))
    
    subscription_types = get_subscription_types()
    enum_values = subscription_types['data']['__type']['enumValues']
    return render_template('new_subscription.html', subscription_types=enum_values)