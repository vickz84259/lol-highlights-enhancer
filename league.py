import re
import subprocess
import time

import PySide2.QtCore as QtCore


class LeagueNotRunningException(Exception):
    """Exception Raised if the League Client is not running
    """


class ProcessCheckerThread(QtCore.QThread):
    status = QtCore.Signal(str)

    def __init__(self):
        super().__init__()

    def exit(self):
        self.running = False
        self.wait()

    def run(self):
        self.running = True

        while self.running:
            try:
                get_process()
            except LeagueNotRunningException:
                self.status.emit('not_running')
            else:
                self.status.emit('running')
                self.running = False
            finally:
                time.sleep(1)


def get_process():
    """ Checks if the League Client is running

    The funcion determines whether the client is running and returns a string
    containing the commandline arguments that were passed when the client was
    being launched.

    Returns:
        A string (the string is empty if the client isn't running)

    Raises:
        LeagueNotRunningException
    """

    # Using the WMIC command to retrieve running processes.
    cmd = 'WMIC PROCESS get Caption,Commandline'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

    result = ''
    for line in proc.stdout:
        line = line.decode('utf-8')

        if 'LeagueClientUx.exe' in line:
            # Formatting the string for easier processing
            result = re.sub(' +', ' ', line).rstrip()
            break

    proc.terminate()
    if not result:
        raise LeagueNotRunningException

    return result


def get_connection_details():
    """ Retrieves the info required to connect to the LCU Api

    The function returns the port and the authentication token that the League
    client that is currenly running is using for its api

    Returns:
        A tuple containing the token(string) and the port(string)
    """

    command_line = get_process()

    token = re.search(r'\"--remoting-auth-token=(\S+)\"',
                      command_line).group(1)
    port = re.search(r'\"--app-port=(\S+)\"', command_line).group(1)

    return (token, port)


if __name__ == "__main__":
    print(get_connection_details())
