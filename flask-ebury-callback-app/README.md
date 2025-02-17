# Flask Ebury Callback App

This is a Flask application designed to listen for callbacks from Ebury's API. It processes incoming requests and can be extended to handle various callback scenarios.

## Project Structure

```
flask-ebury-callback-app
├── app
│   ├── __init__.py
│   ├── routes.py
│   └── config.py
├── requirements.txt
├── run.py
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-ebury-callback-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

Before running the application, ensure that you configure the necessary settings in `app/config.py`, including any API keys or secrets required for Ebury's API.

```
class Config:
    EBURY_USERNAME = "email"
    EBURY_PASSWORD = "password"
    EBURY_AUTH_CLIENT_ID= 'client auth id'
    EBURY_AUTH_CLIENT_SECRET= 'client secret'
    EBURY_REDIRECT_URL = "your OpenID connect redirect url"

    EBURY_AUTHENTICATION_URL = "https://auth-sandbox.ebury.io/"
    EBURY_API_URL = "https://sandbox.ebury.io/"

    DEBUG = True  # Set to False in production
    TESTING = False  # Set to True for testing environment
```

## Running the Application

To start the Flask application, run:
```
gunicorn -w 4 -b 127.0.0.1:5000 "app:create_app()"
```
or if using vscode use Debug tools

The application will start listening for callbacks from Ebury's API on the specified port.

To make public so the url can be access externally, use ngrok https://ngrok.com/
Sign up for an endpoint and get your token, then install and run 

```
pip install ngrok
ngrok config add-authtoken {token}
ngrok http 5000
```
## Usage

Once the application is running, it will process incoming callbacks as defined in `app/routes.py`. You can extend the functionality by adding more routes or processing logic as needed.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.