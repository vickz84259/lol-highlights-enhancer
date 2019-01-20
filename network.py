import base64

import requests

import data_manager as ds


def get_auth_header(token):
    # Creating the authorization header
    auth = f'riot:{token}'.encode()
    b64encoded = base64.b64encode(auth).decode()
    authorization_header = f'Basic {b64encoded}'

    return authorization_header


def __request(relative_url, method, data=None):
    token, port = ds.DataStore.get_connection_details()
    base_url = f'https://127.0.0.1:{port}'
    url = f'{base_url}{relative_url}'

    headers = {
        'Authorization': get_auth_header(token),
        'Accept': 'application/json'}

    if method == 'GET':
        response = requests.get(url, headers=headers, verify=False)
    elif method == 'POST':
        response = requests.post(url, headers=headers, verify=False, data=data)

    return response.json()


def get(relative_url):
    return __request(relative_url, 'GET')


def post(relative_url, data=None):
    return __request(relative_url, 'POST', data=data)
