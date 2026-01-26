import json
import os
from datetime import datetime, timedelta

TOKEN_FILE = 'xero_tokens.json'

def save_tokens(access_token, refresh_token, expires_in, tenant_id=None):
    """Save tokens to JSON file with expiry timestamp."""
    expires_at = (datetime.now() + timedelta(seconds=expires_in)).timestamp()
    data = {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_at': expires_at,
        'tenant_id': tenant_id or os.environ.get('XERO_TENANT_ID')
    }
    with open(TOKEN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def load_tokens():
    """Load tokens from JSON file. Returns None if file doesn't exist."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, 'r') as f:
        return json.load(f)

def is_token_valid():
    """Check if access token exists and hasn't expired."""
    tokens = load_tokens()
    if not tokens:
        return False

    # Check if expired (with 5-minute buffer)
    expires_at = tokens.get('expires_at', 0)
    return datetime.now().timestamp() < (expires_at - 300)

def get_access_token():
    """Get current access token, refresh if needed."""
    tokens = load_tokens()
    if not tokens:
        return None

    # If token is still valid, return it
    if is_token_valid():
        return tokens['access_token']

    # Token expired, refresh it
    return refresh_access_token()

def refresh_access_token():
    """Refresh the access token using refresh token."""
    import requests
    import base64

    tokens = load_tokens()
    if not tokens or not tokens.get('refresh_token'):
        return None

    # Token refresh endpoint
    XERO_TOKEN_URL = 'https://identity.xero.com/connect/token'
    XERO_CLIENT_ID = os.environ.get('XERO_CLIENT_ID')
    XERO_CLIENT_SECRET = os.environ.get('XERO_CLIENT_SECRET')

    credentials = f"{XERO_CLIENT_ID}:{XERO_CLIENT_SECRET}"
    auth_header = f"Basic {base64.b64encode(credentials.encode()).decode()}"

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': tokens['refresh_token']
    }

    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        response = requests.post(XERO_TOKEN_URL, data=data, headers=headers)
        response.raise_for_status()
        token_response = response.json()

        # Save new tokens
        save_tokens(
            token_response['access_token'],
            token_response['refresh_token'],
            token_response['expires_in'],
            tokens.get('tenant_id')
        )

        return token_response['access_token']
    except Exception as e:
        print(f"Token refresh failed: {e}")
        return None

def clear_tokens():
    """Delete token file."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
