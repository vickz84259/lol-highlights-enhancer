import json
import ssl
import time

import websocket
import PySide2.QtCore as QtCore

from data_manager import DataStore
import network

file = None


class WebSocketThread(QtCore.QThread):
    api_event = QtCore.Signal(list)

    def __init__(self):
        super().__init__()

    def exit(self):
        self.ws.close()
        self.wait()

    def on_message(self, message):
        if message:
            msg = json.loads(message)
            self.api_event.emit(msg)

    def on_error(self, error):
        pass

    def on_close(self):
        pass

    def on_open(self):
        endpoints = [
            'OnJsonApiEvent_lol-gameflow_v1_gameflow-phase',
            'OnJsonApiEvent_lol-gameflow_v1_watch'
        ]
        for endpoint in endpoints:
            self.ws.send(json.dumps([5, endpoint]))

    def run(self):
        token, port = DataStore.get_connection_details()

        time.sleep(5)
        self.ws = websocket.WebSocketApp(
            f"wss://127.0.0.1:{port}/",
            header={'Authorization': network.get_auth_header(token)},
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)

        self.ws.run_forever(
            sslopt={'cert_reqs': ssl.CERT_NONE}, suppress_origin=True)


if __name__ == "__main__":
    websocket.enableTrace(True)

    thread = WebSocketThread()
    thread.start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        thread.exit()
