import PySide2.QtCore as QtCore
import requests

from data_manager import DataStore
import utils


class Thread(QtCore.QThread):
    status = QtCore.Signal(str)
    done_status = QtCore.Signal()

    def __init__(self, highlights):
        super().__init__()

        self.highlights = highlights

    def exit(self):
        self.running = False
        self.wait()

    def run(self):
        self.running = True

        match_ids = set()
        for details in self.highlights.values():
            match_id = details['match_id']
            if match_id is not None:
                region = details['region']
                match_ids.add((region, match_id))

        no_of_ids = len(match_ids)
        retrieved = {}
        for x, (region, match_id) in enumerate(match_ids, 1):
            if not self.running:
                break

            url = f'https://slick.co.ke/v1/match/{region}/{match_id}'
            match_details = requests.get(url).json()
            retrieved[match_id] = match_details

            self.status.emit(
                f'Retrieving match details: {round((x/no_of_ids) * 100, 1)}%')

        no_of_highlights = len(self.highlights)
        summoner_name = DataStore.get_preferences()['user_name']

        index = 1
        for name, details in self.highlights.items():
            match_id = details['match_id']
            if match_id in retrieved:
                full_details = retrieved[match_id]

                game_mode = full_details['gameMode']
                queue_id = full_details['queueId']
                mode = utils.get_mode(game_mode, queue_id)
                self.highlights[name]['game_mode'] = mode

                for participant in full_details['participantIdentities']:
                    if participant['player']['summonerName'] == summoner_name:
                        participant_id = participant['participantId']

                for participant in full_details['participants']:
                    if participant['participantId'] == participant_id:

                        champion_id = participant['championId']
                        champion_name = DataStore.get_champion_by_id(
                            champion_id)
                        self.highlights[name]['played_as'] = champion_name
                        self.highlights[name]['win'] = \
                            participant['stats']['win']

            percentage = round((index/no_of_highlights) * 100)
            self.status.emit(
                f'Processing highlights: {percentage}%')
            index += 1

        DataStore.save_partial_highlights(self.highlights, to_file=True)

        self.status.emit('Done')
        self.done_status.emit()
