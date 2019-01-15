import base64
import json
import ssl

import websocket
import PySide2.QtCore as QtCore

import league

file = None


def on_message(ws, message):
    if message:
        print(json.loads(message))


def on_error(ws, error):
    pass


def on_close(ws):
    pass


def on_open(ws):
    ws.send(json.dumps([5, 'OnJsonApiEvent']))


def get_authorization_header(token):
    # Creating the authorization header
    auth = f'riot:{token}'.encode()
    b64encoded = base64.b64encode(auth).decode('ascii')
    authorization_header = f'Basic {b64encoded}'

    return authorization_header


class WebSocketThread(QtCore.QThread):

    def __init__(self):
        super().__init__()

    def exit(self):
        self.ws.close()
        self.wait()

    def run(self):
        token, port = league.get_connection_details()

        self.ws = websocket.WebSocketApp(
            f"wss://127.0.0.1:{port}/",
            header={'Authorization': get_authorization_header(token)},
            on_open=on_open,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close)

        self.ws.run_forever(
            sslopt={'cert_reqs': ssl.CERT_NONE}, suppress_origin=True)


if __name__ == "__main__":
    websocket.enableTrace(True)

    thread = WebSocketThread()
    thread.start()

    while True:
        pass
