import requests

from data_manager import DataStore
import utils

BASE_URL = 'https://api.gfycat.com/v1'


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
    token = DataStore.get_gfycat_token()
    auth_header = {'Authorization': f'Bearer {token}'}

    url = f'{BASE_URL}/gfycats'
    response = requests.post(url, json=body, headers=auth_header)

    gfyname = response.json()['gfyname']
    upload_url = f'https://filedrop.gfycat.com/{gfyname}'

    with open(file_path, 'rb') as video:
        response = requests.put(upload_url, video)

    video_url = f'https://gfycat.com/{gfyname}'
    return video_url
