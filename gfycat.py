import requests
from ruamel.yaml import YAML

import utils

BASE_URL = 'https://api.gfycat.com/v1'


def get_token():
    """Function to get api token

    The api token is required to authenticate api calls made to gfycat

    returns:
        String representing the api token received.
    """
    with open('config.yaml') as config_file:
        yaml = YAML(typ='safe')
        config = yaml.load(config_file)

    client_id = config['gfycat']['client_id']
    client_secret = config['gfycat']['client_secret']

    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(f'{BASE_URL}/oauth/token', json=body)
    token = response.json()['access_token']

    print(token)
    return token


def upload(file_path):
    """Uploads a video to gfycat

    Args:
        file_path (string): Path to the video to be uploaded.

    Returns:
        A string representing the url to the uploaded video.
    """
    filename = utils.get_filename(file_path)
    body = {
        'title': filename,
        'tags': ['leagueoflegends', 'League of Legends']
    }
    auth_header = {'Authorization': f'Bearer {get_token()}'}

    url = f'{BASE_URL}/gfycats'
    response = requests.post(url, json=body, headers=auth_header)

    gfyname = response.json()['gfyname']
    upload_url = f'https://filedrop.gfycat.com/{gfyname}'

    with open(file_path, 'rb') as video:
        response = requests.put(upload_url, video)
        print(response)

    video_url = f'https://gfycat.com/{gfyname}'
    return video_url
