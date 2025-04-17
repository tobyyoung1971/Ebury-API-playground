class Config:
    # only needed for host to host
    # not needed it you use the ebo login function
    EBURY_USERNAME = "email"
    EBURY_PASSWORD = "password"
    
    # The next three of config variables must be included and must match with those
    # held in the environment you are connecting to 
    EBURY_AUTH_CLIENT_ID= 'client auth id'
    EBURY_AUTH_CLIENT_SECRET= 'client secret'
    EBURY_REDIRECT_URL = "your OpenID connect redirect url"
    # the redirect for the ebo login to work must be
    # EBURY_REDIRECT_URL = "http://127.0.0.1:5000/auth_callback"
    # for this app to work locally

    # These are the urls for the environment to connect to
    EBURY_AUTHENTICATION_URL = "https://auth-sandbox.ebury.io/"
    EBURY_API_URL = "https://sandbox.ebury.io/"
 
    # The secret used to verify the webhook signature
    EBURY_WEBHOOK_SECRET = "your webhook secret"

    DEBUG = True  # Set to False in production
    TESTING = False  # Set to True for testing environment
