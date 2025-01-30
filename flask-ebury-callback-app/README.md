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

## Running the Application

To start the Flask application, run:
```
python run.py
```

The application will start listening for callbacks from Ebury's API on the specified port.

## Usage

Once the application is running, it will process incoming callbacks as defined in `app/routes.py`. You can extend the functionality by adding more routes or processing logic as needed.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.