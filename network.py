import base64

import requests

import league


def get_auth_header(token):
    # Creating the authorization header
    auth = f'riot:{token}'.encode()
    b64encoded = base64.b64encode(auth).decode('ascii')
    authorization_header = f'Basic {b64encoded}'

    return authorization_header


def request(relative_url, method, data=None):
    token, port = league.get_connection_details()
    base_url = f'https://127.0.0.1:{port}'
    url = f'{base_url}{relative_url}'

    headers = {
        'Authorization': get_auth_header(token),
        'Accept': 'application/json'}

    if method == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    elif method == 'POST':
        pass

    return response.json()
