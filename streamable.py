import os.path

import requests


def upload(file_path, username, password):
    """Upload a file to Streamable.com

    Args:
        file_path (string): Path to the video to be uploaded.
        username (string): Streamable username
        password (string): Password to Streamable account

    Returns:
        A string that represents the url to the uploaded video
    """
    with open(file_path, 'rb') as file:
        filename = os.path.splitext(os.path.basename(file_path))[0]
        content = {'file': (filename, file)}

        user_agent = {
            'user-agent': 'lol-highlights-enhancer/1.0.0 '
            '(victor@slick.co.ke)'}

        api_url = 'https://api.streamable.com/upload'
        response = requests.post(
            api_url,
            files=content,
            auth=(username, password),
            headers=user_agent)

    shortcode = response.json()['shortcode']
    video_url = f'https://streamable.com/{shortcode}'

    return video_url
