import base64
import json
import ssl

import websocket

import league

file = None


def on_message(ws, message):
    file.write(message.strip('\n'))


def on_error(ws, error):
    file.write(error)


def on_close(ws):
    file.write("### closed ###")


def on_open(ws):
    global file
    file = open('websocket.log', 'w')
    ws.send(json.dumps([5, 'OnJsonApiEvent']))


if __name__ == "__main__":
    websocket.enableTrace(True)

    token, port = league.get_connection_details()

    # Creating the authorization header
    auth = f'riot:{token}'.encode()
    b64encoded = base64.b64encode(auth).decode('ascii')
    authorization_header = f'Basic {b64encoded}'

    ws = websocket.WebSocketApp(
        f"wss://127.0.0.1:{port}/",
        header={'Authorization': authorization_header},
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)

    ws.on_open = on_open
    try:
        ws.run_forever(
            sslopt={'cert_reqs': ssl.CERT_NONE}, suppress_origin=True)
    finally:
        if file is not None:
            file.close()
