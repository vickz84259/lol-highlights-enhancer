import requests

from data_manager import DataStore
import utils


def upload(file_path):
    """Upload a file to Streamable.com

    Args:
        file_path (string): Path to the video to be uploaded.

    Returns:
        A string that represents the url to the uploaded video
    """
    with open(file_path, 'rb') as file:
        filename = utils.get_filename(file_path)
        content = {'file': (filename, file)}

        auth = DataStore.get_streamable_secrets()
        headers = {
            'user-agent': 'lol-highlights-enhancer/1.0.0 '
            '(victor@slick.co.ke)',
            'Authorizaion': f'Basic {auth}'}

        api_url = 'https://api.streamable.com/upload'
        response = requests.post(
            api_url,
            files=content,
            headers=headers)

    shortcode = response.json()['shortcode']
    video_url = f'https://streamable.com/{shortcode}'

    return video_url
