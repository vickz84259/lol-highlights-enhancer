import os
import os.path
import re
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import PySide2.QtCore as QtCore

import utils


class HighlightsWatchThread(QtCore.QThread, FileSystemEventHandler):
    highlight_created = QtCore.Signal(str)

    def __init__(self, path):
        super().__init__()

        self.path = path
        self.highlights = []

    def __get_int_trail(self, file_name):
        return int(re.search(r'_(\d{2})', file_name).group(1))

    def __sub_trail(self, new_trail, file_name):
        return re.sub(r'_\d{2}', f'_{new_trail}', file_name)

    def __rename(self, old_name, new_name):
        old_file = os.path.join(self.path, old_name)
        new_file = os.path.join(self.path, new_name)

        os.rename(old_file, new_file)

    def __cleanup(self):
        for file_name in self.highlights:
            old_trail = self.__get_int_trail(file_name)
            new_name = self.__sub_trail(str(old_trail - 1).zfill(2), file_name)

            self.__rename(file_name, new_name)

    def on_created(self, event):
        new_path = event.src_path
        file_name = utils.get_filename(new_path, with_extension=True)

        if not utils.is_highlight(file_name):
            return

        if self.highlights:
            old_number = self.__get_int_trail(self.highlights[-1])
            new_number = old_number + 1
        else:
            trailing_number = self.__get_int_trail(file_name)
            new_number = trailing_number + 1

        new_trail = str(new_number).zfill(2)
        new_name = self.__sub_trail(new_trail, file_name)
        self.highlights.append(new_name)

        # Necessary sleep to give the client time to release hold on
        # highlight file
        time.sleep(1.5)
        self.__rename(file_name, new_name)

    def exit(self):
        self.observer.stop()
        self.observer.join()

        self.__cleanup()

        self.running = False
        self.wait()

    def run(self):
        self.running = True

        self.observer = Observer()
        self.observer.schedule(self, self.path)
        self.observer.start()

        while self.running:
            time.sleep(1)


if __name__ == "__main__":
    thread = HighlightsWatchThread(
        'C:/Users/user/Documents/League of Legends/Highlights')
    thread.start()

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        thread.exit()
