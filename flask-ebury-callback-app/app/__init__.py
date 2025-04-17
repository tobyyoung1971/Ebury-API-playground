from flask import Flask
from flask_socketio import SocketIO
from app.ebury_api import start_token_watcher

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.bp)

    # Initialize SocketIO for the auto refreshing of the 'callbacks' page
    socketio.init_app(app)

    # Start the token watcher in a separate thread, this refreshes 
    # the access token when it gets close to expiry
    start_token_watcher(app)

    return app