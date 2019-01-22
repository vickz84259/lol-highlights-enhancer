import time

import PySide2.QtCore as QtCore

from data_manager import DataStore
import network


class Thread(QtCore.QThread):
    done_setup = QtCore.Signal()
    login_status = QtCore.Signal(str)

    def __init__(self, is_first_time):
        super().__init__()

        self.is_first_time = is_first_time

    def exit(self):
        self.wait()

    def run(self):
        self.running = True

        while self.running:
            login_status = network.get('/lol-summoner/v1/current-summoner')

            if login_status.get('httpStatus') is not None:
                self.login_status.emit(
                    'Not logged in. Please Log in to the client')
                time.sleep(2)
                continue
            else:
                self.login_status.emit('Logged in.')

                if self.is_first_time:
                    DataStore.setup()
                    self.done_setup.emit()

                self.running = False
