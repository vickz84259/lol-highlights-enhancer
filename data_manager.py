import base64
import time

from ruamel.yaml import YAML
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Util import Padding

import keyring
import requests

import league
import network
import utils

PREFERENCES_PATH = 'resources\\user_preferences.yaml'
HIGHLIGHTS_PATH = 'highlights.yaml'
CHAMPIONS_PATH = 'resources\\champions.json'

PLATFORM = 'lol-highlights-enhancer'


class DataStore():
    connection_details = None

    __internal_data = {
        'preferences': {'file_name': PREFERENCES_PATH, 'data': None},
        'highlights': {'file_name': HIGHLIGHTS_PATH, 'data': None},
        'champions': {'file_name': CHAMPIONS_PATH, 'data': None}}

    @classmethod
    def __save(cls, data, type, to_file=False):
        file_name = cls.__internal_data[type]['file_name']
        if to_file:
            with open(file_name, 'w') as file:
                yaml = YAML(typ='safe')
                yaml.dump(data, file)

        cls.__internal_data[type]['data'] = data

    @classmethod
    def __get(cls, type):
        file_name = cls.__internal_data[type]['file_name']
        data = cls.__internal_data[type]['data']

        if data is None:
            with open(file_name) as file:
                yaml = YAML(typ='safe')
                cls.__internal_data[type]['data'] = yaml.load(file)

        return cls.__internal_data[type]['data']

    @classmethod
    def get_preferences(cls):
        return cls.__get('preferences')

    @classmethod
    def get_highlights(cls):
        return cls.__get('highlights')

    @classmethod
    def get_champions(cls):
        return cls.__get('champions')

    @classmethod
    def save_preferences(cls, data, to_file=False):
        cls.__save(data, 'preferences', to_file)

    @classmethod
    def save_highlights(cls, data, to_file=False):
        cls.__save(data, 'highlights', to_file)

    @classmethod
    def save_champions(cls, data, to_file=False):
        cls.__save(data, 'champions', to_file)

    @classmethod
    def __get_latest_token(cls):
        client_id, client_secret = cls.get_gfycat_secrets()
        body = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret
        }

        base_url = 'https://api.gfycat.com/v1'
        url = f'{base_url}/oauth/token'
        response = requests.post(url, json=body)

        return response.json()

    @classmethod
    def __is_expired(cls, expiry):
        result = False

        current_time = time.time()
        if current_time >= float(expiry):
            result = True

        return result

    @classmethod
    def get_gfycat_token(cls):
        token = keyring.get_password(PLATFORM, 'gfycat_token')
        expiry = keyring.get_password(PLATFORM, 'expiry')

        if token is None or cls.__is_expired(expiry):
            token_details = cls.__get_latest_token()
            token = token_details['access_token']
            expiry = time.time() + token_details['expires_in']

            keyring.set_password(PLATFORM, 'gfycat_token', token)
            keyring.set_password(PLATFORM, 'expiry', expiry)

        return token

    @classmethod
    def get_gfycat_secrets(cls):
        key = keyring.get_password(PLATFORM, 'puuid')
        client_id = keyring.get_password(PLATFORM, 'client_id')
        client_secret = keyring.get_password(PLATFORM, 'client_secret')

        return (cls.decrypt(key, client_id), cls.decrypt(key, client_secret))

    @classmethod
    def get_streamable_secrets(cls):
        key = keyring.get_password(PLATFORM, 'puuid')
        auth = keyring.get_password(PLATFORM, 'Authorization')

        return cls.decrypt(key, auth)

    @classmethod
    def setup(cls):
        cls.setup_preferences()
        cls.setup_highlights()
        cls.setup_champions()

        cls.setup_client_secrets()

    @classmethod
    def setup_client_secrets(cls):
        preferences = cls.get_preferences()

        user_name = preferences['user_name']
        region = preferences['region']
        url = f'https://slick.co.ke/v1/summoner/{region}/{user_name}'

        summoner_details = requests.get(url).json()
        keyring.set_password(PLATFORM, 'puuid', summoner_details['puuid'])

        gfycat = summoner_details['secrets']['gfycat']
        keyring.set_password(PLATFORM, 'client_id', gfycat['client_id'])
        keyring.set_password(PLATFORM, 'client_secret',
                             gfycat['client_secret'])

        streamable = summoner_details['secrets']['streamable']
        keyring.set_password(PLATFORM, 'Authorization',
                             streamable['Authorization'])

    @classmethod
    def setup_preferences(cls):
        current_summoner = network.get('/lol-summoner/v1/current-summoner')
        user_name = current_summoner['displayName']

        highlights_folder = network.get(
            '/lol-highlights/v1/highlights-folder-path')

        preferences = cls.get_preferences()

        preferences['first_time'] = False
        preferences['user_name'] = user_name
        preferences['current-highlights-folder'] = highlights_folder
        preferences['lol-highlights-folder'].append(highlights_folder)

        region = network.get(
            '/lol-platform-config/v1/namespaces/LoginDataPacket/platformId')
        region = 'na1' if region == 'NA' else region.lower()
        preferences['region'] = region

        normalised_region = network.get(
            '/lol-platform-config/v1/namespaces/LoginDataPacket/'
            'competitiveRegion')
        preferences['normalised_region'] = normalised_region.lower()

        cls.save_preferences(preferences, to_file=True)

    @classmethod
    def setup_highlights(cls):
        highlights = network.post('/lol-highlights/v1/highlights')

        highlights_dict = {}
        for highlight in highlights:
            name = highlight['name']
            result = utils.get_match_details(name)

            if result is not None:
                highlight['region'] = result['region'].lower()
                highlight['match_id'] = result['match_id']

                patch_major = result['patch_major']
                patch_minor = result['patch_minor']
                highlight['patch_version'] = f'{patch_major}.{patch_minor}'
            else:
                highlight['region'] = None
                highlight['match_id'] = None
                highlight['patch_version'] = None

            highlight['gfycat'] = None
            highlight['streamable'] = None

            highlights_dict[name] = highlight

        cls.save_highlights(highlights_dict, to_file=True)

    @classmethod
    def refresh_highlights(cls):
        highlights = network.post('/lol-highlights/v1/highlights')

        old_highlights = cls.get_highlights()
        for highlight in highlights:

            name = highlight['name']
            if name not in old_highlights:
                result = utils.get_match_details(name)
                if result is not None:
                    highlight['region'] = result['region'].lower()
                    highlight['match_id'] = result['match_id']

                    patch_major = result['patch_major']
                    patch_minor = result['patch_minor']
                    highlight['patch_version'] = f'{patch_major}.{patch_minor}'
                else:
                    highlight['region'] = None
                    highlight['match_id'] = None
                    highlight['patch_version'] = None

                highlight['gfycat'] = None
                highlight['streamable'] = None

                old_highlights[name] = highlight

        cls.save_highlights(old_highlights, to_file=True)

    @classmethod
    def setup_champions(cls):
        preferences = cls.get_preferences()
        region = preferences['normalised_region']
        url = f'https://ddragon.leagueoflegends.com/realms/{region}.json'

        latest_version = requests.get(url).json()['n']['champion']
        base_url = 'https://ddragon.leagueoflegends.com/cdn/'
        url = f'{base_url}{latest_version}/data/en_US/champion.json'
        champions = requests.get(url).json()

        cls.save_champions(champions, to_file=True)

    @classmethod
    def get_connection_details(cls):
        if cls.connection_details is None:
            connection_details = league.get_connection_details()

        return connection_details

    @classmethod
    def decrypt(cls, key, data):
        bytes_input = base64.b64decode(data.encode())

        block_size = 16
        nonce = bytes_input[:block_size]
        tag = bytes_input[block_size:block_size * 2]
        ciphertext = bytes_input[block_size * 2:]

        key = SHA256.new(key.encode()).digest()
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        padded_data = cipher.decrypt_and_verify(ciphertext, tag)

        data = Padding.unpad(padded_data, block_size).decode()
        return data

    @classmethod
    def get_highlight_names(cls):
        return list(cls.get_highlights().keys())

    @classmethod
    def get_highlight(cls, name):
        return cls.get_highlights().get(name)

    @classmethod
    def save_highlight(cls, highlight_name, data):
        highlight_dict = {}
        highlight_dict[highlight_name] = data

        cls.save_partial_highlights(highlight_dict, to_file=True)

    @classmethod
    def get_champion_by_id(cls, id):
        champions = cls.get_champions()

        for champion, champion_data in champions['data'].items():
            if int(champion_data['key']) == id:
                return champion_data['name']

    @classmethod
    def save_partial_highlights(cls, highlights, to_file=False):
        base_highlights = cls.get_highlights()
        for highlight_name, data in highlights.items():
            base_highlights[highlight_name] = data

        cls.save_highlights(base_highlights, to_file)
