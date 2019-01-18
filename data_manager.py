import re

from ruamel.yaml import YAML

import league
import network

PREFERENCES_PATH = 'resources\\user_preferences.yaml'
HIGHLIGHTS_PATH = 'highlights.yaml'


class DataStore():
    connection_details = None

    __internal_data = {
        'preferences': {'file_name': PREFERENCES_PATH, 'data': None},
        'highlights': {'file_name': HIGHLIGHTS_PATH, 'data': None}}

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
    def save_preferences(cls, data, to_file=False):
        cls.__save(data, 'preferences', to_file)

    @classmethod
    def save_highlights(cls, data, to_file=False):
        cls.__save(data, 'highlights', to_file)

    @classmethod
    def setup(cls):
        cls.setup_preferences()
        cls.setup_highlights()

    @classmethod
    def setup_preferences(cls):
        current_summoner = network.request(
            '/lol-summoner/v1/current-summoner', 'GET')
        user_name = current_summoner['displayName']

        highlights_folder = network.request(
            '/lol-highlights/v1/highlights-folder-path', 'GET')

        preferences = cls.get_preferences()

        preferences['first_time'] = False
        preferences['user_name'] = user_name
        preferences['current-highlights-folder'] = highlights_folder
        preferences['lol-highlights-folder'].append(highlights_folder)

        cls.save_preferences(preferences, to_file=True)

    @classmethod
    def setup_highlights(cls):
        highlights = network.request('/lol-highlights/v1/highlights', 'POST')

        for highlight in highlights:
            name = highlight['name']
            regex = re.match(r'\d+-\d+_(\w{2,3}\d?)-(\d+)_\d{2}', name)

            if regex is not None:
                highlight['region'] = regex.group(1)
                highlight['match_id'] = regex.group(2)
            else:
                highlight['region'] = None
                highlight['match_id'] = None

        cls.save_highlights(highlights, to_file=True)

    @classmethod
    def get_connection_details(cls):
        if cls.connection_details is None:
            connection_details = league.get_connection_details()

        return connection_details
