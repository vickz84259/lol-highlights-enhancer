import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer
import PySide2.QtCore as QtCore


class HighlightsWatchThread(QtCore.QThread, FileSystemEventHandler):

    def __init__(self, path):
        super().__init__()

        self.path = path

    def on_created(self, event):
        print(event.src_path)

    def exit(self):
        self.observer.stop()
        self.observer.join()

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
