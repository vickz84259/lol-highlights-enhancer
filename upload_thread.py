import queue
import time

import PySide2.QtCore as QtCore

from data_manager import DataStore
import gfycat
import streamable


class Thread(QtCore.QThread):
    uploaded = QtCore.Signal(tuple)

    def __init__(self, q):
        super().__init__()

        self.q = q

    def exit(self):
        self.running = False
        self.wait()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def run(self):
        self.running = True
        self.is_paused = False

        while self.running:
            try:
                highlight_name, platform = self.q.get(timeout=1)

                while self.is_paused:
                    time.sleep(5)

                highlight = DataStore.get_highlight(highlight_name)

                file_path = highlight['filepath']
                if platform == 'gfycat':
                    video_url = gfycat.upload(file_path)
                elif platform == 'streamable':
                    video_url = streamable.upload(file_path)

                self.uploaded.emit((highlight_name, video_url))
            except queue.Empty:
                continue
