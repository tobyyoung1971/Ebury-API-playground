import requests
from urllib.parse import urlencode, urlparse, parse_qs
from flask import current_app
from base64 import b64encode, urlsafe_b64decode
import time
import json

access_token = None
refresh_token = None
token_expiration = 0
clients = []

def get_ebo_login():
    clientid = current_app.config['EBURY_AUTH_CLIENT_ID']
    url = current_app.config['EBURY_AUTHENTICATION_URL'] + "authenticate?scope=openid&response_type=code&state=state&redirect_uri=" + current_app.config['EBURY_REDIRECT_URL'] + "&client_id=" + clientid 

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.get(url, headers=headers, allow_redirects=True)
    if response.status_code == 200:
        return response.text
    else:
        response.raise_for_status()

def get_access_token():
    global access_token, refresh_token, token_expiration
    if access_token is None or time.time() >= token_expiration:
        if refresh_token:
            auth_response = refresh_ebury_token(refresh_token)
        else:
            auth_response = login_ebury()
        access_token = get_ebury_token(auth_response)
    return access_token

def login_ebury():
    email = current_app.config['EBURY_USERNAME']
    password = current_app.config['EBURY_PASSWORD']
    clientid = current_app.config['EBURY_AUTH_CLIENT_ID']
    url = current_app.config['EBURY_AUTHENTICATION_URL'] + "login"
    state = "random_state"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "email": email,
        "password": password,
        "client_id": clientid,
        "state": state
    }

    response = requests.post(url, headers=headers, data=data, allow_redirects=False)
    
    if response.status_code == 302:
        redirect_url = response.headers.get('Location')
        if redirect_url:
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            code = query_params.get('code', [None])[0]
            if code:
                return {'code': code}
            else:
                raise ValueError("Code not found in the redirect URL")
        else:
            raise ValueError("Redirect URL not found in the response headers")
    else:
        raise ValueError(f"Unexpected response status code: {response.status_code}")

def get_ebury_token(auth_response):
    code = auth_response.get('code')
    if not code:
        raise ValueError("Login response does not contain 'code'")
    
    clientid = current_app.config['EBURY_AUTH_CLIENT_ID']
    clientsecret = current_app.config['EBURY_AUTH_CLIENT_SECRET']
    redirecturl = current_app.config['EBURY_REDIRECT_URL']
    url = current_app.config['EBURY_AUTHENTICATION_URL'] + "token"

    headers = {
        "Authorization": f"Basic {b64encode(f'{clientid}:{clientsecret}'.encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirecturl
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        # get the access token and set the expiration time.
        token_response = response.json()
        global access_token, token_expiration
        access_token = token_response.get('access_token')
        refresh_token = token_response.get('refresh_token')
        token_expiration = time.time() + token_response.get('expires_in', 3600) - 60  # Refresh 1 minute before expiration

        # Extract the clients information from the JSON web token id_token
        # and store them in global variable for later use.
        id_token = token_response.get('id_token')
        if id_token:
                id_token_parts = id_token.split('.')
                id_token_payload = json.loads(urlsafe_b64decode(id_token_parts[1] + '==').decode())
                global clients
                clients = id_token_payload.get('clients', [])
        
        return access_token
    else:
        response.raise_for_status()

def refresh_ebury_token(refresh_token):
    clientid = current_app.config['EBURY_AUTH_CLIENT_ID']
    clientsecret = current_app.config['EBURY_AUTH_CLIENT_SECRET']
    url = current_app.config['EBURY_AUTHENTICATION_URL'] + "token"

    headers = {
        "Authorization": f"Basic {b64encode(f'{clientid}:{clientsecret}'.encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def get_clients():
    global clients
    access_token = get_access_token()
    if access_token is None:
        raise ValueError("Access token not found")
    else:
        return clients

def get_ebury_balance():
    global clients
    access_token = get_access_token()
    balances = {}
    
    for client in clients:
        client_id = client.get('client_id')
        url = current_app.config['EBURY_API_URL'] + "balances?client_id=" + client_id
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            balances[client_id] = response.json()
        else:
            response.raise_for_status()
    
    return balances


def get_webhook_subscriptions():
    access_token = get_access_token()
    webhooks = {}
    url = current_app.config['EBURY_API_URL'] + "webhooks/graphql"
    global clients
    for client in clients:
        client_id = client.get('client_id')
        urlclient_id = url + "?client_id=" + client_id
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Client-ID": client_id
        }
        query = {
            "query": """
            {
                subscriptions {
                    totalCount
                    nodes {
                        id
                        createdAt
                        url
                        active
                        types
                    }
                }
            }
            """
        }
        
        response = requests.post(urlclient_id, headers=headers, json=query)
        
        if response.status_code == 200:
            webhooks[client_id] = response.json()
        else:
            response.raise_for_status()

    return webhooks

def delete_webhook_subscription(subscription_id):
    access_token = get_access_token()
    url = current_app.config['EBURY_API_URL'] + "webhooks/graphql?client_id=" + clients[0].get('client_id')
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    query = {
        "query": """
        mutation {
            deleteSubscription(input: {id: "%s"}) {
                subscription {
                    id
                }
            }
        }
        """ % subscription_id
    }
    
    response = requests.post(url, headers=headers, json=query)
    
    if response.status_code == 200:
        return {'status': 'success'}
    else:
        response.raise_for_status()

def disable_webhook_subscription(subscription_id):
    access_token = get_access_token()
    url = current_app.config['EBURY_API_URL'] + "webhooks/graphql?client_id=" + clients[0].get('client_id')
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    query = {
        "query": """
        mutation {
            updateSubscription(input: {id: "%s", patch: {active: false}}) {
                subscription {
                    id
                    active
                }
            }
        }
        """ % subscription_id
    }
    
    response = requests.post(url, headers=headers, json=query)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def get_subscription_types():
    access_token = get_access_token()
    url = current_app.config['EBURY_API_URL'] + "webhooks/graphql?client_id=" + clients[0].get('client_id')
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    
    query = {
            "query": """
            {
                __type(name: "WebhookType") {
                    name
                    enumValues {
                        name
                    }
                }
                webhookTypes
            }
            """
        }
    
    response = requests.post(url, headers=headers, json=query)
    
    if response.status_code == 200:
        response_json = response.json()
        print("Subscription Types Response:", response_json)  # Log the response
        return response_json
    else:
        response.raise_for_status()

def create_subscription(client_id, callback_url, types, secret):
    access_token = get_access_token()
    url = current_app.config['EBURY_API_URL'] + "webhooks/graphql?client_id=" + client_id
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Format the types array as a list of enum values
    formatted_types = "["+ ', '.join([f'{type}' for type in types])+"]"
    
    
    query = {
        "query": """
        mutation {
            createSubscription(input: {subscription: {url: "%s", types: %s, active: true, secret: "%s"}}) {
                subscription {
                    id
                    url
                    types
                    active
                }
            }
        }
        """ % (callback_url, formatted_types, secret)
    }
    
    response = requests.post(url, headers=headers, json=query)
    
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

