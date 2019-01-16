from ruamel.yaml import YAML

import league
import network

PREFERENCES_PATH = 'resources\\user_preferences.yaml'


class DataStore():
    preferences = None
    connection_details = None

    @classmethod
    def get_preferences(cls):
        if cls.preferences is None:
            with open(PREFERENCES_PATH) as preferences_file:
                yaml = YAML(typ='safe')
                cls.preferences = yaml.load(preferences_file)

        return cls.preferences

    @classmethod
    def save_preferences(cls, data, to_file=False):
        if to_file:
            with open(PREFERENCES_PATH, 'w') as preferences_file:
                yaml = YAML(typ='safe')
                yaml.dump(data, preferences_file)

        cls.preferences = data

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
    def get_connection_details(cls):
        if cls.connection_details is None:
            connection_details = league.get_connection_details()

        return connection_details
