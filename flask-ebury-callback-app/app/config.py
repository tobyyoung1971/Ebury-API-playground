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
