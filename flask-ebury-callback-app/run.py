from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
   # app.run(debug=True)
   # Using 0.0.0.0 to ensure resolution to both localhost and 127.0.0.1
   socketio.run(app, debug=True, host='0.0.0.0', port=5001)